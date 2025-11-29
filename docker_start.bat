@echo off
chcp 65001 >nul
echo ========================================
echo 图片审查系统 - Docker 容器启动
echo ========================================
echo.

echo [1/2] 正在启动 Docker 容器...
docker-compose up -d

if %errorlevel% neq 0 (
    echo.
    echo [错误] 容器启动失败！
    echo 请检查：
    echo   1. Docker 是否正常运行
    echo   2. 端口 8501 是否被占用
    echo   3. 是否已构建镜像（运行 docker_build.bat）
    pause
    exit /b 1
)

echo.
echo [2/2] 等待容器启动完成...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 容器启动成功！
echo ========================================
echo.
echo 访问地址：
echo   HTTPS: https://localhost:8501
echo   HTTP:  http://localhost:8501
echo.
echo 其他操作：
echo   - 查看日志: docker-compose logs -f
echo   - 停止容器: docker_stop.bat
echo   - 重启容器: docker-compose restart
echo.
pause

