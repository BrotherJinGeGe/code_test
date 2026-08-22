# PyVideoEditor 打包指南

本项目已配置好 PyInstaller 打包脚本，可以将 Python 代码打包成独立的可执行文件。

## 快速打包

### Linux/macOS

```bash
cd video_editor
./build.sh
```

### Windows

```bash
cd video_editor
python -m PyInstaller pyinstaller.spec
```

## 手动打包步骤

### 1. 安装依赖

```bash
pip install pyside6 pyinstaller
```

### 2. 确保资源目录存在

```bash
mkdir -p resources/icons
```

### 3. 执行打包

```bash
pyinstaller --clean pyinstaller.spec
```

### 4. 获取可执行文件

打包完成后，可执行文件位于：
- **Linux**: `dist/PyVideoEditor`
- **Windows**: `dist/PyVideoEditor.exe`
- **macOS**: `dist/PyVideoEditor.app`

## 打包配置文件说明

`pyinstaller.spec` 文件包含以下关键配置：

- **入口文件**: `main.py`
- **包含的二进制文件**: ffmpeg（视频处理工具）
- **数据文件**: resources 目录（图标等资源）
- **隐藏导入**: PySide6 相关模块和项目内部模块
- **输出名称**: PyVideoEditor
- **窗口模式**: 无控制台窗口（GUI 应用）

## 注意事项

1. **ffmpeg 依赖**: 打包时会自动包含系统的 ffmpeg，确保系统已安装 ffmpeg
2. **资源文件**: 如果项目使用了图标等资源文件，请放在 `resources` 目录下
3. **跨平台**: 需要在目标操作系统上分别打包
4. **文件大小**: 由于包含 PySide6 和 ffmpeg，打包后的文件较大（约 150MB+）

## 运行打包后的程序

```bash
# Linux
./dist/PyVideoEditor

# Windows
dist\PyVideoEditor.exe

# macOS
open dist/PyVideoEditor.app
```

## 故障排除

### 问题：找不到某些模块

解决：在 `pyinstaller.spec` 的 `hiddenimports` 列表中添加缺失的模块

### 问题：运行时缺少资源文件

解决：确保资源文件在 `datas` 配置中正确声明

### 问题：程序启动后立即退出

解决：使用 `console=True` 重新打包，查看控制台错误信息
