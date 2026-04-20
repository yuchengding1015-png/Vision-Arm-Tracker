# kinematics.py
import math
import numpy as np
import config as cfg

class KinematicsSolver:
    def __init__(self):
        self.filtered_x = 0.0
        self.filtered_y = 0.0
        self.filtered_z = 0.0
        self.filtered_GrabOpen = 0.0
        self.is_first_frame = True

    def solve(self, raw_x, raw_y, raw_z, raw_GrabOpen):
        """执行限幅、滤波并计算 IK 角度"""
        
        # 1. 坐标限幅与低通滤波
        if self.is_first_frame:
            self.filtered_x, self.filtered_y, self.filtered_z = raw_x, raw_y, raw_z
            self.filtered_GrabOpen = raw_GrabOpen
            self.is_first_frame = False
        else:
            if abs(raw_x - self.filtered_x) > cfg.MAX_JUMP: 
                raw_x = self.filtered_x + math.copysign(cfg.MAX_JUMP, raw_x - self.filtered_x)
            if abs(raw_y - self.filtered_y) > cfg.MAX_JUMP: 
                raw_y = self.filtered_y + math.copysign(cfg.MAX_JUMP, raw_y - self.filtered_y)
            if abs(raw_z - self.filtered_z) > cfg.MAX_JUMP: 
                raw_z = self.filtered_z + math.copysign(cfg.MAX_JUMP, raw_z - self.filtered_z)

            self.filtered_x = (raw_x * cfg.SMOOTH_FACTOR) + (self.filtered_x * (1.0 - cfg.SMOOTH_FACTOR))
            self.filtered_y = (raw_y * cfg.SMOOTH_FACTOR) + (self.filtered_y * (1.0 - cfg.SMOOTH_FACTOR))
            self.filtered_z = (raw_z * cfg.SMOOTH_FACTOR) + (self.filtered_z * (1.0 - cfg.SMOOTH_FACTOR))
            self.filtered_GrabOpen = (raw_GrabOpen * cfg.SMOOTH_FACTOR) + (self.filtered_GrabOpen * (1.0 - cfg.SMOOTH_FACTOR))

        # 2. 逆运动学 (IK) 解算
        targetBase_math = math.degrees(math.atan2(self.filtered_x, self.filtered_z))
        target_R = math.hypot(self.filtered_x, self.filtered_z) 
        target_Y = self.filtered_y
        
        absolute_pitch = np.clip(target_Y * 300.0, -90.0, 0.0)
        pitch_rad = math.radians(absolute_pitch)
        
        wrist_R = target_R - cfg.ARM_L3 * math.cos(pitch_rad)
        wrist_y = target_Y - cfg.ARM_L3 * math.sin(pitch_rad)
        wrist_R = max(0.01, wrist_R) 
        
        D = math.hypot(wrist_R, wrist_y)
        D_MAX = cfg.ARM_L1 + cfg.ARM_L2 - 0.002       
        D_MIN = abs(cfg.ARM_L1 - cfg.ARM_L2) + 0.002  
        
        if D > D_MAX:
            ratio = D_MAX / D
            wrist_R *= ratio; wrist_y *= ratio; D = D_MAX
        elif D < D_MIN:
            ratio = D_MIN / D
            wrist_R *= ratio; wrist_y *= ratio; D = D_MIN
            
        cos_upper = (cfg.ARM_L1**2 + D**2 - cfg.ARM_L2**2) / (2 * cfg.ARM_L1 * D)
        targetUpper_math = math.degrees(math.atan2(wrist_y, wrist_R) - math.acos(cos_upper))
        
        cos_top = (cfg.ARM_L1**2 + cfg.ARM_L2**2 - D**2) / (2 * cfg.ARM_L1 * cfg.ARM_L2)
        targetTop_math = 180 - math.degrees(math.acos(cos_top))
        
        targetFore_math = absolute_pitch - (targetUpper_math + targetTop_math)
        
        targetUpper_math = np.clip(targetUpper_math, 2.0, 90.0)
        targetTop_math   = np.clip(targetTop_math, 2.0, 90.0)
        targetFore_math  = np.clip(targetFore_math, -60.0, 60.0)

        # 3. 计算最终发送角度
        final_Base  = (targetBase_math * cfg.DIR_BASE + cfg.OFFSET_BASE) % 360.0
        final_Upper = targetUpper_math * cfg.DIR_UPPER + cfg.OFFSET_UPPER
        final_Top   = targetTop_math * cfg.DIR_TOP + cfg.OFFSET_TOP
        final_Fore  = targetFore_math * cfg.DIR_FORE + cfg.OFFSET_FORE

        return {
            "Base": final_Base, "Upper": final_Upper, "Top": final_Top, 
            "Fore": final_Fore, "ClawX": cfg.OFFSET_CLAW_X,
            "f_x": self.filtered_x, "f_y": self.filtered_y, "f_z": self.filtered_z,
            "f_grab": self.filtered_GrabOpen
        }