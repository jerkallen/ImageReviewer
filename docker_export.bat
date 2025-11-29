@echo off
chcp 65001 >nul
echo ========================================
echo 图片审查系统 - Docker 镜像导出
echo ========================================
echo.

set OUTPUT_FILE=image_reviewer.tar

echo [1/2] 正在导出 Docker 镜像...
echo 目标文件: %OUTPUT_FILE%
echo.

docker save -o %OUTPUT_FILE% image_reviewer:latest

if %errorlevel% neq 0 (
    echo.
    echo [错误] 镜像导出失败！
    echo 请确认镜像是否已构建（运行 docker_build.bat）
    pause
    exit /b 1
)

echo.
echo [2/2] 计算文件大小...
for %%A in (%OUTPUT_FILE%) do set FILE_SIZE=%%~zA

echo.
echo ========================================
echo 镜像导出成功！
echo ========================================
echo.
echo 文件信息：
echo   文件名: %OUTPUT_FILE%
echo   大小:   %FILE_SIZE% 字节
echo.
echo 使用说明：
echo   将此文件复制到目标机器后，运行：
echo   docker load -i %OUTPUT_FILE%
echo.
pause

