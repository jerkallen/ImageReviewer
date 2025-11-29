@echo off
chcp 65001 >nul
echo ========================================
echo 图片审查系统 - Docker 容器日志
echo ========================================
echo.
echo 按 Ctrl+C 退出日志查看
echo.
docker-compose logs -f

