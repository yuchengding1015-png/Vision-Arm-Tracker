# config.py

# ================= 1. 机械臂物理尺寸 (总长 49cm) =================
ARM_L1 = 0.20  
ARM_L2 = 0.13  
ARM_L3 = 0.16  
BASE_OFFSET_Z = 0.75  
BASE_OFFSET_Y = 0.08  

# ================= 2. 真实机械臂连接与协议 =================
ENABLE_REAL_ARM = True  
COM_PORT = 'COM9'       
BAUDRATE = 115200

# ================= 3. Unity 转向与姿态校准区 =================
DIR_BASE  = 1    
DIR_UPPER = -1    
DIR_TOP   = 1    
DIR_FORE  = -1   

OFFSET_BASE = -90  
OFFSET_UPPER = 60 
OFFSET_TOP = 0      
OFFSET_FORE = 0    
OFFSET_CLAW_X = 0   

# ================= 4. 双重滤波与防抖配置区 =================
SMOOTH_FACTOR = 0.60    # 指数平滑系数 (越小越平滑)
MAX_JUMP = 0.04        # 限幅器：单帧最大允许跳变距离 (米)

# ================= 5. 网络通信配置 =================
UDP_IP = "127.0.0.1"
UDP_PORT = 5052