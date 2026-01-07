# 容器镜像构建文件
# 兼容性: Podman / Docker (OCI 标准)
# 基础镜像: Python 3.12 Slim (Debian)

FROM python:3.12-slim

WORKDIR /app

# 安装OpenSSL和其他依赖
RUN apt-get update && apt-get install -y \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖（使用清华源加速）
COPY requirements.txt .
# 禁用代理，避免构建时连接问题
# ENV HTTP_PROXY="" HTTPS_PROXY="" http_proxy="" https_proxy=""
# RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip download -d ./packages -r requirements.txt

# 复制应用程序文件
COPY app.py .
COPY run_app.py .
COPY config.json .
COPY config_handler.py .
COPY database.py .
COPY image_handler.py .
COPY user_handler.py .
COPY generate_cert.py .

# 复制静态文件和模板
COPY static ./static
COPY templates ./templates

# 创建证书目录
RUN mkdir -p certs

# 创建数据目录结构
RUN mkdir -p /data/logs /data/images

# 暴露端口（HTTP/HTTPS）
EXPOSE 8501

# 启动应用
# 注意: 自动重启策略在 docker-compose.yml 中配置 (restart: always)
CMD ["python", "run_app.py"]

