@echo off
chcp 65001 >nul
title 比格多栋 - 打包EXE

echo.
echo =======================================
echo   比格多栋 EXE 打包工具
echo =======================================
echo.

:: 检查Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 没有检测到 Python！
    echo.
    echo 请先安装 Python 3.7 或更高版本
    echo 下载: https://www.python.org/downloads/
    echo 安装时记得勾选 "Add Python to PATH"
    pause
    exit /b 1
)
echo [OK] Python 检测完毕
echo.

:: 安装依赖
echo [1/3] 安装打包工具...
pip install pyinstaller -q
if %ERRORLEVEL% NEQ 0 (
    echo 安装失败！请检查网络
    pause
    exit /b 1
)
echo [OK]
echo.

:: 清理旧文件
echo [2/3] 清理旧文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del /q *.spec
echo [OK]
echo.

:: 打包
echo [3/3] 正在打包（约1-3分钟）...
echo.
pyinstaller --onefile --windowed --name "比格多栋" ^
    --hidden-import PyQt5.sip ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtGui ^
    --hidden-import PyQt5.QtWidgets ^
    --add-data "beagle_sprite.png;." ^
    --add-data "beagle_sprite_flip.png;." ^
    --add-data "beagle_icon.png;." ^
    beagle_pet.py

if %ERRORLEVEL% NEQ 0 (
    echo 打包失败！
    pause
    exit /b 1
)
echo [OK] 打包成功！
echo.

:: 整理
mkdir "dist\比格多栋_v1.0" 2>nul
if exist "dist\比格多栋.exe" move "dist\比格多栋.exe" "dist\比格多栋_v1.0\" >nul
copy README.md "dist\比格多栋_v1.0\" >nul 2>&1

echo.
echo =======================================
echo   打包完成！
echo.
echo   输出: dist\比格多栋_v1.0\
echo   文件: 比格多栋.exe
echo.
echo   把 比格多栋.exe 发给朋友，
echo   对方双击就能用！不需要装Python！
echo =======================================
echo.
pause
