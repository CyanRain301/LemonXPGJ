@echo off
echo ================================
echo   Flask 图片管理工具
echo ================================
echo.

REM 获取当前目录
set PROJECT_DIR=%~dp0

REM 延迟2秒后打开浏览器（等待服务器启动）
start /B cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

REM 启动 Flask 服务器
call "%PROJECT_DIR%venv\Scripts\python" "%PROJECT_DIR%app.py"


pause