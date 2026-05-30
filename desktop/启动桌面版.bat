@echo off
chcp 65001 >nul
title Word 引用插入 - 桌面版

cd /d "%~dp0"

echo ========================================
echo   Word 引用插入 - 桌面版
echo ========================================
echo.
echo   [使用说明]
echo   1. 先打开 Word 并新建/打开一个文档
echo   2. 本程序启动后会自动连接 Word
echo   3. 粘贴参考文献 -> 解析 -> 点击条目插入脚注
echo.

echo 正在启动...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [X] 启动失败，请确认已安装 Python 和 pywin32
    echo     pip install pywin32
    pause
)
