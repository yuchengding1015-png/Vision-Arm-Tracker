@echo off
:: 设置终端为黑底绿字，赛博科技感拉满！

:: 【极其关键】：调用 .venv 里的 python.exe 来运行 Jarvis_System 里的 main.py
:: 使用 /MIN 会让黑窗口启动后自动最小化，不挡住 Unity 界面
start "AI_Core_Engine" /MIN ".\.venv\Scripts\python.exe" ".\python_src\main.py"


:: 强制等待 5 秒，给深度相机启动、对齐画面留出充足的时间
timeout /t 5 /nobreak > NUL

:: ⚠️ 【请修改这里】：把 ".\Unity_App\Jibot.exe" 换成你真实的 Unity exe 的路径和名字！
start "" ".\unity_app\My project.exe"

timeout /t 3 /nobreak > NUL
exit