# hardware.py
import serial
import time

class RobotArm:
    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2) # 等待下位机初始化

    # hardware.py
    def move_all(self, servos, time_ms=50):
        """
        严格按照 #{ID}P{PWM}T{TIME}! 逐条发送，并加入物理延时防堵塞。
        """
        safe_time = max(50, int(time_ms))
        
        for i, pwm in enumerate(servos):
            cmd = f"#{i:03d}P{int(pwm):04d}T{safe_time:04d}!"
            self.ser.write(cmd.encode('ascii'))
            self.ser.flush()
            time.sleep(0.005) # 5ms 硬件防溢出缓冲延时

    def close(self):
        self.ser.close()

def angle_to_pwm(angle, angle_min, angle_max, pwm_min, pwm_max):
    """通用的角度转 PWM 映射函数"""
    lower = min(angle_min, angle_max)
    upper = max(angle_min, angle_max)
    angle = max(lower, min(angle, upper))
    if angle_max == angle_min: 
        return pwm_min
    return int((angle - angle_min) * (pwm_max - pwm_min) / (angle_max - angle_min) + pwm_min)