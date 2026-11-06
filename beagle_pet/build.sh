#!/bin/bash
# 比格多栋桌面宠物 - Linux 打包脚本
# Beagle Desktop Pet Builder for Linux

echo "====================================="
echo "  比格多栋桌面宠物 - 打包工具"
echo "  Beagle Desktop Pet Builder"
echo "====================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3！"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi

# Install dependencies
echo "[1/4] 检查依赖..."
python3 -m pip install --upgrade pip -q
python3 -m pip install PyQt5 pyinstaller -q

if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败！"
    exit 1
fi
echo "[OK] 依赖安装完成"
echo ""

# Clean old builds
echo "[2/4] 清理旧的构建文件..."
rm -rf dist build *.spec 2>/dev/null
echo "[OK] 清理完成"
echo ""

# Build with PyInstaller
echo "[3/4] 正在打包，请耐心等待..."
echo "  (通常需要 1-3 分钟)"
echo ""

pyinstaller --onefile --windowed --name "BeaglePet" \
    --hidden-import PyQt5.sip \
    --hidden-import PyQt5.QtCore \
    --hidden-import PyQt5.QtGui \
    --hidden-import PyQt5.QtWidgets \
    beagle_pet.py

if [ $? -ne 0 ]; then
    echo "[错误] 打包失败！"
    exit 1
fi
echo "[OK] 打包完成！"
echo ""

# Create distribution folder
echo "[4/4] 创建分发包..."
mkdir -p "dist/BeaglePet_v1.0"
mv "dist/BeaglePet" "dist/BeaglePet_v1.0/" 2>/dev/null || \
mv "dist/beagle_pet" "dist/BeaglePet_v1.0/" 2>/dev/null
cp README.md "dist/BeaglePet_v1.0/" 2>/dev/null
cp requirements.txt "dist/BeaglePet_v1.0/" 2>/dev/null

echo "[OK] 分发包已创建！"
echo ""
echo "====================================="
echo "  打包成功！"
echo "  输出位置: dist/BeaglePet_v1.0/"
echo "====================================="
