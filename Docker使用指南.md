# Docker 部署快速使用指南

## 一、前置准备

### 1. 安装 Docker

- Windows: 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Linux: 参考 [Docker 官方文档](https://docs.docker.com/engine/install/)

### 2. 验证 Docker 安装

打开命令行，运行：

```bash
docker --version
docker-compose --version
```

如果能正常显示版本号，说明安装成功。

## 二、快速部署（Windows）

### 方式一：使用批处理脚本（推荐）

#### 1. 构建镜像

双击运行 `docker_build.bat`，等待构建完成。

#### 2. 启动容器

双击运行 `docker_start.bat`，启动成功后会显示访问地址。

#### 3. 访问应用

在浏览器中打开：
- HTTPS: `https://localhost:8501`
- HTTP: `http://localhost:8501`

#### 4. 查看日志（可选）

双击运行 `docker_logs.bat`，实时查看应用日志。

#### 5. 停止容器

双击运行 `docker_stop.bat`。

### 方式二：使用命令行

打开命令行，在项目目录执行：

```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

## 三、镜像导出与导入

### 导出镜像（用于离线部署）

双击运行 `docker_export.bat`，会在当前目录生成 `image_reviewer.tar` 文件。

### 导入镜像

将 `image_reviewer.tar` 复制到目标机器，然后执行：

```bash
docker load -i image_reviewer.tar
```

## 四、离线部署

如果目标机器无法访问互联网：

1. 在联网机器上构建并导出镜像
2. 将以下文件复制到目标机器：
   - `image_reviewer.tar` （镜像文件）
   - `docker-compose.offline.yml`
   - `certs` 目录（如果已生成）
   - `data` 目录

3. 在目标机器上导入镜像：
   ```bash
   docker load -i image_reviewer.tar
   ```

4. 启动容器：
   ```bash
   docker-compose -f docker-compose.offline.yml up -d
   ```

## 五、数据管理

### 数据存储位置

所有数据都存储在 `./data` 目录下：
- `data/images/` - 图片文件
- `data/logs/` - 日志文件
- `data/app.db` - 数据库文件

### 数据备份

定期备份 `./data` 目录即可：

```bash
# 压缩备份
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# 或使用 Windows 压缩工具直接压缩 data 文件夹
```

### 数据恢复

将备份的 `data` 目录解压到项目根目录，然后重启容器。

## 六、常见问题

### 1. 端口被占用

**错误信息**：`Bind for 0.0.0.0:8501 failed: port is already allocated`

**解决方法**：
- 检查端口占用：`netstat -ano | findstr 8501`
- 关闭占用端口的程序，或修改 `docker-compose.yml` 中的端口映射

### 2. 容器无法启动

**解决方法**：
1. 查看日志：双击 `docker_logs.bat`
2. 确认 Docker Desktop 正在运行
3. 确认镜像已构建：运行 `docker images | findstr image_reviewer`

### 3. 浏览器提示证书不安全

这是正常现象，因为使用的是自签名证书。

**解决方法**：
- Chrome: 点击"高级" → "继续前往"
- Firefox: 点击"高级" → "接受风险并继续"
- Edge: 点击"高级" → "继续前往"

### 4. 无法连接到应用

**解决方法**：
1. 确认容器正在运行：`docker-compose ps`
2. 检查防火墙设置，确保允许 8501 端口
3. 尝试使用 `http://127.0.0.1:8501` 访问

## 七、高级配置

### 修改端口

1. 编辑 `config.json`，修改 `port` 值
2. 编辑 `docker-compose.yml`，修改 `ports` 配置
3. 重新构建并启动：
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### 使用外部数据目录

编辑 `docker-compose.yml`，修改 volumes 配置：

```yaml
volumes:
  - ./certs:/app/certs
  - /path/to/your/data:/data  # 改为你的实际路径
```

### 查看容器资源占用

```bash
docker stats image_reviewer
```

## 八、运维命令

```bash
# 查看容器状态
docker-compose ps

# 重启容器
docker-compose restart

# 进入容器
docker-compose exec image-reviewer /bin/bash

# 查看最近100行日志
docker-compose logs --tail=100

# 完全清理（包括数据卷）
docker-compose down -v

# 查看镜像大小
docker images image_reviewer
```

## 九、更新应用

```bash
# 停止并删除容器
docker-compose down

# 重新构建镜像
docker-compose build

# 启动新容器
docker-compose up -d
```

## 十、性能优化

### 1. 限制容器资源

编辑 `docker-compose.yml`，添加资源限制：

```yaml
services:
  image-reviewer:
    # ... 其他配置 ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 2. 日志轮转

编辑 `docker-compose.yml`，添加日志配置：

```yaml
services:
  image-reviewer:
    # ... 其他配置 ...
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 十一、安全建议

1. **生产环境使用正式证书**：替换自签名证书为正式的 SSL 证书
2. **定期备份数据**：使用定时任务定期备份 `data` 目录
3. **限制访问**：配置防火墙，只允许特定 IP 访问
4. **定期更新**：及时更新 Docker 镜像和依赖包
5. **监控日志**：定期检查应用日志，及时发现异常

## 十二、技术支持

- 详细文档：查看 `DOCKER_README.md`
- 项目文档：查看 `README.md`
- Docker 官方文档：https://docs.docker.com/

