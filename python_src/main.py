# main.py
import cv2
import pyrealsense2 as rs
import numpy as np
import mediapipe as mp
import time
import os
import urllib.request
import socket
import math
import threading
import queue

# 导入拆分后的模块
import config as cfg


from hardware import RobotArm, angle_to_pwm
from kinematics import KinematicsSolver
from visualizer import draw_scifi_hud
from tracker import SpatialHandTracker 

def init_mediapipe():
    model_path = 'hand_landmarker.task'
    if not os.path.exists(model_path):
        print("正在下载 MediaPipe 模型...")
        urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", model_path)
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
        running_mode=mp.tasks.vision.RunningMode.VIDEO, 
        num_hands=5) # 依然保留检测多只手的能力
    return mp.tasks.vision.HandLandmarker.create_from_options(options)

def main():
    # 1. 初始化各类模块
    ik_solver = KinematicsSolver()
    hand_tracker = SpatialHandTracker(max_lost_frames=15) # 🔴 新增：实例化目标追踪器大脑
    landmarker = init_mediapipe()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (cfg.UDP_IP, cfg.UDP_PORT)

    real_bot = None
    cmd_queue = queue.Queue(maxsize=1) 

    def serial_worker():
        while True:
            data = cmd_queue.get()
            if data is None: 
                break
            servos, dt_ms = data
            if real_bot:
                real_bot.move_all(servos, time_ms=dt_ms)

    if cfg.ENABLE_REAL_ARM:
        try:
            real_bot = RobotArm(cfg.COM_PORT, cfg.BAUDRATE)
            print("✅ 真实机械臂连接成功！")
            threading.Thread(target=serial_worker, daemon=True).start()
        except Exception as e:
            print(f"❌ 机械臂连接失败: {e}")
            cfg.ENABLE_REAL_ARM = False

    # 2. 启动 RealSense 相机
    pipeline = rs.pipeline()
    rs_config = rs.config()
    rs_config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    rs_config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    align = rs.align(rs.stream.color)

    try:
        profile = pipeline.start(rs_config)
        depth_intrinsics = rs.video_stream_profile(profile.get_stream(rs.stream.depth)).get_intrinsics()
        print("✅ 相机启动成功！请把手掌对准镜头...")
    except Exception as e:
        print(f"❌ 相机启动失败！详情: {e}")
        return

    last_timestamp = 0
    last_send_time = time.time()

    # 3. 主循环
    try:
        while True:
            try: frames = pipeline.wait_for_frames(timeout_ms=3000)
            except RuntimeError: continue
                
            aligned_frames = align.process(frames)
            color_frame, depth_frame = aligned_frames.get_color_frame(), aligned_frames.get_depth_frame()
            if not color_frame or not depth_frame: continue
                
            img = np.asanyarray(color_frame.get_data())
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
            
            timestamp = int(time.time() * 1000)
            if timestamp <= last_timestamp: timestamp = last_timestamp + 1
            last_timestamp = timestamp
            
            result = landmarker.detect_for_video(mp_image, timestamp)
            h, w, _ = img.shape

            ik_res = None

            # 将检测到的所有手交给 tracker 去筛选，直接吐出锁定的手和坐标
            valid_hand, target_px, target_py = hand_tracker.update(result.hand_landmarks, w, h)

            # 4. 手部后续处理逻辑
            if valid_hand:
                wrist, thumb_tip, index_tip = valid_hand[0], valid_hand[4], valid_hand[8]
                
                # 捏合计算
                pinch_dist = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)
                raw_GrabOpen = max(-40.0, min(40.0, (pinch_dist - 0.02) * 800 - 40))

                # 深度中值滤波
                depths =[]
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        py_c, px_c = target_py + dy, target_px + dx
                        if 0 <= py_c < h and 0 <= px_c < w:
                            d = depth_frame.get_distance(px_c, py_c)
                            if 0 < d < 2.0: depths.append(d)
                
                depth_value = np.median(depths) if depths else 0

                if depth_value > 0: 
                    # 3D 反投影
                    real_3d = rs.rs2_deproject_pixel_to_point(depth_intrinsics,[target_px, target_py], depth_value)
                    raw_x = real_3d[0] 
                    raw_z = cfg.BASE_OFFSET_Z - real_3d[2]  
                    raw_y = cfg.BASE_OFFSET_Y - real_3d[1]  

                    ik_res = ik_solver.solve(raw_x, raw_y, raw_z, raw_GrabOpen)

                    # 打包发送 Unity
                    data_string = f"{ik_res['Base']},{ik_res['Upper']},{ik_res['Top']},{ik_res['Fore']},{ik_res['ClawX']},{ik_res['f_grab']},{ik_res['f_x']},{ik_res['f_y']},{ik_res['f_z']}"
                    sock.sendto(data_string.encode(), server_address)

                    # 异步发送真实机械臂
                    if cfg.ENABLE_REAL_ARM and real_bot:
                        current_time = time.time()
                        dt_ms = int((current_time - last_send_time) * 1000)
                        dt_ms = max(30, min(150, dt_ms)) 
                        last_send_time = current_time
                        
                        pwm_s0 = angle_to_pwm(ik_res['Base'], 0, 180, 2150, 850)
                        pwm_s1 = angle_to_pwm(ik_res['Upper'], -90, 90, 900, 2100)
                        pwm_s2 = angle_to_pwm(ik_res['Fore'], -90, 90, 2100, 900)
                        pwm_s3 = angle_to_pwm(ik_res['Top'], -90, 90, 900, 2100)
                        pwm_s4 = 1500
                        pwm_s5 = angle_to_pwm(ik_res['f_grab'], -40, 40, 1600, 950)

                        if cmd_queue.full():
                            try: cmd_queue.get_nowait() 
                            except queue.Empty: pass
                        
                        cmd_queue.put(([pwm_s0, pwm_s1, pwm_s2, pwm_s3, pwm_s4, pwm_s5], dt_ms))

            # 5. 可视化渲染
            img = cv2.flip(img, 1) 
            if valid_hand and ik_res is not None:
                # 传入已经被过滤、锁定的目标手进行画图
                draw_scifi_hud(img, valid_hand, w, h, target_px, target_py, ik_res)

            cv2.imshow("Sci-Fi Holographic IK Solution", img)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

    finally:
        if cfg.ENABLE_REAL_ARM and real_bot: 
            cmd_queue.put(None) 
            time.sleep(0.1)
            real_bot.close()
        landmarker.close()
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()