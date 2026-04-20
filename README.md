# 🤖 Vision-Arm-Tracker: Vision-Based Somatosensory Robotic Arm Control System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange.svg)
![RealSense](https://img.shields.io/badge/Intel%20RealSense-Supported-blue)
![License](https://img.shields.io/badge/License-MIT-green.svg)

This project is a spatial somatosensory robotic arm control system based on the **Intel RealSense depth camera** and **MediaPipe**. By capturing the 3D coordinates of the human hand in real-time via computer vision, computing Inverse Kinematics (IK), and applying smooth filtering, it **synchronously drives both a real physical robotic arm and a virtual Unity robotic arm** (Digital Twin).

*(Insert a screenshot or a GIF demonstrating the robotic arm following your hand movements here)*
> **Tip:** Upload a GIF named `demo.gif` to your repository and replace this line with `![Demo](demo.gif)`.

---

## ✨ Features

- 🖐️ **Spatial Multi-Target Tracking**: Features an independent `tracker.py` module equipped with a spatial distance memory algorithm. It firmly locks onto the initial target hand in multi-person/multi-hand scenarios, completely preventing the robotic arm from sudden jumping or jittering.
- 📐 **3D Inverse Kinematics (IK) Solver**: Combines depth-map deprojection to accurately map the 3D spatial coordinates (X, Y, Z) of the palm to precise rotation angles for the 4 axes of the robotic arm.
- 🛡️ **Dual Anti-Jitter & Smooth Filtering**: Integrates an amplitude limiter and Exponential Moving Average (EMA) filtering to eliminate minor hand tremors, ensuring silky-smooth robotic movements.
- ⚡ **Non-Blocking Asynchronous Communication**: The low-level hardware driver utilizes independent threading and command queues (`Queue`), eliminating serial communication lag and achieving ultra-low latency.
- 🌌 **Sci-Fi Holographic UI**: Renders a real-time high-tech skeletal tracking system and a cyber-radar lock-on UI using OpenCV.
- 🌐 **Digital Twin Ready**: Streams real-time pose data to the local network via UDP protocol, allowing seamless integration with 3D engines like Unity.

---

## 🛠️ Hardware & Software Requirements

### 1. Hardware
- **Depth Camera**: Intel RealSense series (D435 / D435i recommended, requires a USB 3.0 port).
- **Robotic Arm**: A 6-DOF robotic arm control board that supports the `#{ID}P{PWM}T{TIME}!` serial communication protocol (e.g., Lobot, Hiwonder, etc.).
- **PC**: Windows, macOS, or Linux.

### 2. Software & Dependencies
**Python 3.8 - 3.10** is highly recommended for best compatibility. Run the following commands in your terminal to install dependencies:

```bash
# 1. Install core computer vision and math libraries
pip install opencv-python mediapipe numpy

# 2. Install official RealSense SDK
pip install pyrealsense2

# 3. Install serial communication library (⚠️ WARNING: Do NOT install the library named "serial"!)
pip install pyserial
```

> **⚠️ Common Pitfall Guide:**
> If you encounter the error `module 'serial' has no attribute 'Serial'`, it means you accidentally installed the wrong `serial` library.
> **Fix**: Run `pip uninstall serial -y`, and then run `pip install pyserial`.

---

## 🚀 Quick Start

### Step 1: Clone the Repository
```bash
git clone https://github.com/YourUsername/YourRepoName.git
cd YourRepoName
```

### Step 2: Hardware Connection & Configuration
1. Connect the RealSense camera and the robotic arm's control board to your PC via USB.
2. Open the `config.py` file and modify the following parameters according to your setup:
   ```python
   ENABLE_REAL_ARM = True   # Enable real physical robotic arm control
   COM_PORT = 'COM3'        # Usually COMx on Windows, or /dev/ttyUSBx on Mac/Linux
   BAUDRATE = 115200        # Baud rate of your robotic arm controller
   ```

### Step 3: Run the Main Program
```bash
python main.py
```
*Note: The MediaPipe hand-tracking model (a few MBs) will be automatically downloaded on the first run. Please ensure you have an internet connection.*

---

## 📂 Project Structure

The project adopts a highly cohesive and loosely coupled modular design for easy secondary development:

```text
├── main.py          # Main controller: Integrates camera streaming, AI inference, and data routing.
├── config.py        # Configuration center: Arm dimensions, ports, offsets, and tuning parameters.
├── tracker.py       # Spatial tracker: Locks onto the initial target in complex environments to prevent jumping.
├── kinematics.py    # Math brain: Handles 3D Inverse Kinematics (IK) calculation and anti-jitter filtering.
├── hardware.py      # Hardware driver: Manages PWM protocol packing and asynchronous serial communication.
└── visualizer.py    # UI renderer: Draws Sci-Fi holographic skeletons and target radars via OpenCV.
```

---

## 🎮 Control Logic

- **Movement Tracking**: Aim your palm at the camera and move it in 3D space (Up/Down, Left/Right, Forward/Backward). The robotic claw will follow the absolute 3D coordinates of your palm.
- **Grabbing / Pinching**: The program calculates the spatial distance between your **thumb and index fingertip** in real-time.
  - **Pinch Fingers**: The robotic claw closes. UI shows `SYS: LOCKED`.
  - **Open Fingers**: The robotic claw opens. UI shows `SYS: TRACKING`.

<img width="867" height="562" alt="image" src="https://github.com/user-attachments/assets/30ad3b39-5363-4720-85e1-53e9a21e59e0" />

---

## 🔧 Tuning Guide

If the robotic arm's movement does not meet your expectations, you can easily fine-tune it in `config.py`:
- **Movement feels too slow or delayed?** Increase `SMOOTH_FACTOR` (e.g., set to `0.7`).
- **Movement feels too fast or slightly jittery?** Decrease `SMOOTH_FACTOR` (e.g., set to `0.4`).
- **Axis direction reversed?** Flip the sign of `DIR_BASE`, `DIR_UPPER`, etc. (`1` to `-1`).
- **Want to connect to Unity?** Listen to `UDP_IP` and `UDP_PORT` configured in `config.py` within your Unity C# script, and parse the incoming string by splitting it with commas `,`.

---

## 🤝 Contribution & Feedback

Pull Requests and Issues are highly welcome! 
If you find this project helpful, please give it a ⭐️ **Star**! It means a lot to me.

## 📄 License
This project is licensed under the [MIT License](LICENSE).
