@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 CS学习平台 - 临时服务器启动工具
echo 作者：冯宗林 (计科23级)
echo ========================================
echo.

echo 🔍 正在检查环境...

REM 检查是否在Django项目目录
if not exist "manage.py" (
    echo ❌ 未找到manage.py文件
    echo 请在Django项目根目录运行此脚本
    pause
    exit /b 1
)

echo ✅ Django项目检查通过

REM 获取本机IP地址
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "ip=%%a"
    goto :found_ip
)
:found_ip
set "ip=%ip: =%"

echo 🌐 本机IP地址: %ip%
echo.

echo 📋 访问方式：
echo    本地访问: http://localhost:8000
echo    局域网访问: http://%ip%:8000
echo.

echo ⚠️  注意：
echo    - 确保防火墙允许8000端口
echo    - 局域网用户需要在同一WiFi下
echo    - 按 Ctrl+C 停止服务器
echo.

echo 🚀 正在启动Django服务器...
echo.

REM 启动Django服务器
python manage.py runserver 0.0.0.0:8000

echo.
echo 🛑 服务器已停止
pause
