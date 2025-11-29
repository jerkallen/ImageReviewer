@echo off
chcp 65001 >nul
echo ========================================
echo 图片审查系统 - Docker 容器停止
echo ========================================
echo.

echo 正在停止 Docker 容器...
docker-compose down

if %errorlevel% neq 0 (
    echo.
    echo [错误] 容器停止失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 容器已停止！
echo ========================================
echo.
pause

