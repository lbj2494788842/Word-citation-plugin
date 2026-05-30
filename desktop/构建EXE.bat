@echo off
chcp 65001 >nul
title Word引用插入 - 构建EXE

cd /d "%~dp0"

echo ========================================
echo   Word 引用插入 - 打包为 EXE
echo ========================================
echo.

echo [1/2] 正在检查依赖...
pip install pywin32 PyInstaller --quiet 2>nul

echo [2/2] 正在打包（请耐心等待）...
echo.

pyinstaller --onefile --windowed --name "Word引用插入" ^
    --hidden-import win32com ^
    --hidden-import win32com.client ^
    --hidden-import pythoncom ^
    main.py

if errorlevel 1 (
    echo.
    echo [X] 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo   [OK] 打包成功！
echo   输出文件：dist\Word引用插入.exe
echo ========================================
echo.
echo   双击运行即可使用
echo   注意：需要先打开 Word 文档
echo.
pause
