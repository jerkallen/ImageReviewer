@echo off
chcp 65001 >nul
echo ========================================
echo 图片审查系统 - 启动脚本
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境，请先运行以下命令：
    echo python -m venv venv
    echo venv\Scripts\activate
    echo pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM 激活虚拟环境并启动应用
echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [信息] 启动Flask应用...
echo.
venv\Scripts\python.exe run_app.py

REM 如果出错，暂停以便查看错误信息
if errorlevel 1 (
    echo.
    echo [错误] 应用启动失败！
    pause
)

