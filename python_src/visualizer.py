# visualizer.py
import cv2

# 手部骨架连接关系
HAND_CONNECTIONS =[
    (0,1), (1,2), (2,3), (3,4),        
    (0,5), (5,6), (6,7), (7,8),        
    (5,9), (9,10), (10,11), (11,12),   
    (9,13), (13,14), (14,15), (15,16), 
    (13,17), (17,18), (18,19), (19,20),
    (0,17)                             
]

def draw_scifi_hud(img, handLms, w, h, target_px, target_py, ik_res):
    """在图像上绘制科幻 UI 和数据"""
    # 1. 绘制科幻全息手部骨架
    for connection in HAND_CONNECTIONS:
        p1 = handLms[connection[0]]
        p2 = handLms[connection[1]]
        x1, y1 = int((1.0 - p1.x) * w), int(p1.y * h)
        x2, y2 = int((1.0 - p2.x) * w), int(p2.y * h)
        cv2.line(img, (x1, y1), (x2, y2), (180, 100, 0), 4) 
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 0), 2) 

    for lm in handLms:
        lx, ly = int((1.0 - lm.x) * w), int(lm.y * h)
        cv2.circle(img, (lx, ly), 5, (255, 200, 0), cv2.FILLED)

    # 2. 绘制掌心赛博雷达 (由于外部已经做了镜像，需要反转 X 坐标)
    draw_px = w - 1 - target_px
    draw_py = target_py
    cv2.circle(img, (draw_px, draw_py), 8, (0, 0, 255), cv2.FILLED)
    cv2.circle(img, (draw_px, draw_py), 25, (0, 255, 255), 2)
    cv2.line(img, (draw_px-35, draw_py), (draw_px+35, draw_py), (0, 255, 255), 2)
    cv2.line(img, (draw_px, draw_py-35), (draw_px, draw_py+35), (0, 255, 255), 2)

    # 3. 绘制文字信息
    status_color = (0, 255, 0) if ik_res['f_grab'] > 0 else (0, 0, 255)
    status_text = "LOCKED" if ik_res['f_grab'] <= 0 else "TRACKING"
    cv2.putText(img, f"SYS: {status_text}", (draw_px + 30, draw_py - 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
    cv2.putText(img, f"Target XYZ: {ik_res['f_x']:.2f}, {ik_res['f_y']:.2f}, {ik_res['f_z']:.2f} m", 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
    cv2.putText(img, f"Anti-Jitter Filter: ACTIVE", 
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(img, f"Sent-> Up:{ik_res['Upper']:.0f} Top:{ik_res['Top']:.0f} Fore:{ik_res['Fore']:.0f}", 
                (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)