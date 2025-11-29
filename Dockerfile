FROM python:3.12-slim

WORKDIR /app

# 安装OpenSSL和其他依赖
RUN apt-get update && apt-get install -y \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

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

# 暴露端口
EXPOSE 8501

# 启动应用
CMD ["python", "run_app.py"]

