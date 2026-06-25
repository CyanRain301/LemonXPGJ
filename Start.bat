@echo off
chcp 65001 >nul
title 图片管理工具

echo ================================
echo   图片管理工具 v1.0
echo ================================
echo.

set PROJECT_DIR=%~dp0

REM 检查虚拟环境
if not exist "%PROJECT_DIR%venv\Scripts\python.exe" (
    echo 📦 首次运行，正在配置环境...
    python -m venv "%PROJECT_DIR%venv"
    call "%PROJECT_DIR%venv\Scripts\pip" install -r requirements.txt
    echo ✅ 环境配置完成
    echo.
)

echo 🚀 启动服务器...
echo 🌐 正在打开浏览器...

REM 延迟1.5秒后打开浏览器
start /B cmd /c "timeout /t 1 /nobreak >nul && start http://127.0.0.1:5000"

REM 启动 Flask（使用虚拟环境）
call "%PROJECT_DIR%venv\Scripts\python" "%PROJECT_DIR%app.py"

pause