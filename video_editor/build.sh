#!/bin/bash
# PyVideoEditor 打包脚本

set -e

echo "======================================"
echo "PyVideoEditor 打包脚本"
echo "======================================"

# 进入项目目录
cd "$(dirname "$0")"

# 检查依赖
echo ""
echo "检查依赖..."
python3 -m pip list | grep -q pyside6 || {
    echo "安装 PySide6..."
    python3 -m pip install pyside6
}
python3 -m pip list | grep -q pyinstaller || {
    echo "安装 PyInstaller..."
    python3 -m pip install pyinstaller
}

# 创建资源目录（如果不存在）
mkdir -p resources/icons

# 清理旧的构建文件
echo ""
echo "清理旧的构建文件..."
rm -rf build dist __pycache__

# 执行打包
echo ""
echo "开始打包..."
pyinstaller --clean pyinstaller.spec

# 检查打包结果
if [ -f "dist/PyVideoEditor" ]; then
    echo ""
    echo "======================================"
    echo "✓ 打包成功！"
    echo "======================================"
    echo "可执行文件位置：$(pwd)/dist/PyVideoEditor"
    echo "文件大小：$(ls -lh dist/PyVideoEditor | awk '{print $5}')"
    echo ""
    echo "运行程序:"
    echo "  ./dist/PyVideoEditor"
else
    echo ""
    echo "======================================"
    echo "✗ 打包失败！"
    echo "======================================"
    exit 1
fi
