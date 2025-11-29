@echo off
chcp 65001 >nul
echo ========================================
echo 图片审查系统 - Docker 镜像构建
echo ========================================
echo.

echo [1/2] 正在构建 Docker 镜像...
docker-compose build

if %errorlevel% neq 0 (
    echo.
    echo [错误] 镜像构建失败！
    echo 请检查 Docker 是否正常运行。
    pause
    exit /b 1
)

echo.
echo [2/2] 构建完成！
echo.
echo ========================================
echo 镜像构建成功！
echo ========================================
echo.
echo 下一步操作：
echo   - 运行 docker_start.bat 启动容器
echo   - 运行 docker_export.bat 导出镜像
echo.
pause

