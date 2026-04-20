# tracker.py
import math

class SpatialHandTracker:
    def __init__(self, max_lost_frames=15):
        """
        初始化追踪器
        :param max_lost_frames: 允许丢失的最大帧数（超过该帧数则清除记忆）
        """
        self.prev_px = None
        self.prev_py = None
        self.lost_frames = 0
        self.max_lost_frames = max_lost_frames

    def update(self, hand_landmarks_list, w, h):
        """
        传入当前帧检测到的所有手，返回被锁定的那只手及其中心坐标
        """
        # 1. 如果当前画面没手，累加丢失帧数
        if not hand_landmarks_list:
            self.lost_frames += 1
            if self.lost_frames > self.max_lost_frames:
                self.prev_px = None
                self.prev_py = None
            return None, 0, 0

        # 2. 如果画面中有手，重置丢失帧数并开始筛选
        self.lost_frames = 0
        min_dist = float('inf')
        best_hand = None
        best_px, best_py = 0, 0

        for handLms in hand_landmarks_list:
            wrist = handLms[0]
            middle_mcp = handLms[9]
            
            # 计算当前手的掌心坐标
            px = int(((wrist.x + middle_mcp.x) / 2) * w)
            py = int(((wrist.y + middle_mcp.y) / 2) * h)
            px = min(max(px, 0), w - 1)
            py = min(max(py, 0), h - 1)

            # 如果是第一次捕捉（没有记忆），直接锁定第一只手
            if self.prev_px is None:
                best_hand = handLms
                best_px, best_py = px, py
                break
            else:
                # 如果有记忆，寻找距离上一帧位置最近的手
                dist = math.hypot(px - self.prev_px, py - self.prev_py)
                if dist < min_dist:
                    min_dist = dist
                    best_hand = handLms
                    best_px = px
                    best_py = py

        # 3. 更新记忆供下一帧使用
        if best_hand is not None:
            self.prev_px = best_px
            self.prev_py = best_py
        
        return best_hand, best_px, best_py