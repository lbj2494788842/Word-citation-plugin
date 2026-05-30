@echo off
chcp 65001 >nul
echo ========================================
echo   Word 引用插入插件 - 启动
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 正在安装依赖...
if not exist node_modules (
    npm install
    if errorlevel 1 (
        echo 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

echo [2/2] 正在构建并启动服务...
echo.
echo 服务器地址: http://localhost:3000
echo.
echo 请保持此窗口打开
echo.

npm run start
pause
