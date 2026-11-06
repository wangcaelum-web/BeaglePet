@echo off
chcp 65001 >nul
title 比格多栋 - 启动器

echo.
echo =======================================
echo    比格多栋 桌面宠物 - 启动器
echo =======================================
echo.

:: 先看看有没有打包好的exe
if exist "比格多栋.exe" (
    echo 找到打包版！直接运行...
    start "" "比格多栋.exe"
    goto :end
)

:: 检查Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo =======================================
    echo   [错误] 没有检测到 Python！
    echo =======================================
    echo.
    echo 你需要先安装 Python 才能运行本程序。
    echo.
    echo 方法一：安装 Python（推荐）
    echo   1. 打开 https://www.python.org/downloads/
    echo   2. 点击黄色的 "Download Python 3.x"
    echo   3. 运行下载的安装程序
    echo   !!! 一定要勾选 "Add Python to PATH" !!!
    echo   4. 安装完成后重新双击本文件
    echo.
    echo 方法二：找人帮打包成 exe
    echo   把 beagle_pet.py 发给有 Python 的朋友
    echo   让他运行 build.bat 就能生成 exe
    echo   拿到 exe 后直接双击就行
    echo.
    pause
    exit /b 1
)

echo [OK] Python 已检测到
echo.

:: 检查PyQt5
echo 正在检查 PyQt5 图形库...
python -c "import PyQt5" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 首次运行需要安装 PyQt5（自动下载中）...
    pip install PyQt5
    if %ERRORLEVEL% NEQ 0 (
        echo 安装失败！请检查网络连接
        pause
        exit /b 1
    )
    echo PyQt5 安装成功！
) else (
    echo PyQt5 已就绪
)

echo.
echo 正在启动比格多栋...
echo.
echo  使用提示:
echo   左键拖拽 = 移动
echo   双击左键 = 开心蹦跳
echo   右键点击 = 功能菜单
echo   关闭 = 右键菜单选"退出"
echo.

start /MIN python beagle_pet.py

echo 已启动！比格多栋应该出现在你的屏幕上了。
echo 如果看不到，检查任务栏通知区域图标。
echo.

:end
pause
