# Docker 部署说明

## 简介

本文档说明如何使用 Docker 部署图片审查系统。

## 前置要求

- 已安装 Docker
- 已安装 Docker Compose（可选，推荐）

## 快速开始

### 方式一：使用 docker-compose（推荐）

#### 1. 在线部署（首次构建）

```bash
# 构建并启动容器
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

#### 2. 离线部署

如果使用已构建好的镜像：

```bash
# 使用离线配置启动
docker-compose -f docker-compose.offline.yml up -d

# 查看日志
docker-compose -f docker-compose.offline.yml logs -f

# 停止容器
docker-compose -f docker-compose.offline.yml down
```

### 方式二：使用 docker 命令

#### 1. 构建镜像

```bash
docker build -t image_reviewer:latest .
```

#### 2. 运行容器

```bash
docker run -d \
  --name image_reviewer \
  -p 8501:8501 \
  -v ./certs:/app/certs \
  -v ./data:/data \
  -e TZ=Asia/Shanghai \
  -e ROOT_DIRECTORY=/data \
  --restart always \
  image_reviewer:latest
```

## 访问应用

应用启动后，可以通过以下地址访问：

- HTTPS: `https://localhost:8501`
- HTTP: `http://localhost:8501` （如果使用 --no-https 参数启动）

**注意**：首次访问 HTTPS 时，浏览器可能会警告证书不受信任（因为是自签名证书），这是正常的，选择"继续访问"即可。

## 数据持久化

以下目录会被持久化到宿主机：

- `./certs` - SSL证书文件
- `./data` - 应用数据（包括图片、日志、数据库）

## 配置说明

### 端口配置

默认端口为 8501，如需修改：

1. 修改 `config.json` 中的 `port` 配置
2. 修改 `docker-compose.yml` 中的端口映射
3. 重新构建并启动容器

### 数据目录配置

如需使用其他数据目录，修改 `docker-compose.yml` 中的 volumes 配置：

```yaml
volumes:
  - /your/custom/path:/data  # 替换为你的实际路径
```

## 常用命令

### 查看容器状态

```bash
docker-compose ps
```

### 查看容器日志

```bash
# 实时查看日志
docker-compose logs -f

# 查看最近100行日志
docker-compose logs --tail=100
```

### 重启容器

```bash
docker-compose restart
```

### 进入容器

```bash
docker-compose exec image-reviewer /bin/bash
```

### 更新应用

```bash
# 停止并删除容器
docker-compose down

# 重新构建镜像
docker-compose build

# 启动新容器
docker-compose up -d
```

## 镜像导出与导入

### 导出镜像（用于离线部署）

```bash
docker save -o image_reviewer.tar image_reviewer:latest
```

### 导入镜像

```bash
docker load -i image_reviewer.tar
```

## 故障排查

### 容器无法启动

1. 检查端口是否被占用：`netstat -ano | findstr 8501`
2. 查看容器日志：`docker-compose logs`
3. 检查数据目录权限

### 无法访问应用

1. 确认容器正在运行：`docker-compose ps`
2. 检查防火墙设置
3. 确认端口映射正确

### SSL证书问题

容器首次启动时会自动生成SSL证书，如果遇到证书问题：

1. 删除 `./certs` 目录下的所有文件
2. 重启容器，会自动重新生成证书

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| TZ | 时区设置 | Asia/Shanghai |
| ROOT_DIRECTORY | 数据根目录 | /data |

## 安全建议

1. 生产环境建议使用正式的SSL证书替换自签名证书
2. 定期备份 `./data` 目录
3. 不要将敏感信息提交到版本控制系统
4. 定期更新基础镜像和依赖包

