# 容器化部署指南

## 前置要求

### Windows 11 环境（必须）
- **必须安装 Podman Desktop**（禁止使用 Docker Desktop）
- 下载地址：https://podman-desktop.io/downloads
- Podman Desktop 会自动配置 WSL2 后端

### 安装步骤

1. **下载并安装 Podman Desktop**
   - 访问 https://podman-desktop.io/downloads
   - 下载 Windows 版本安装包
   - 运行安装程序，按默认选项安装

2. **初始化 Podman**
   - 启动 Podman Desktop
   - 首次启动会自动初始化 Podman Machine（基于 WSL2）
   - 等待初始化完成

3. **验证安装**
   ```powershell
   podman --version
   podman-compose --version
   ```

### 配置 Docker CLI 别名（推荐）

Podman 完全兼容 Docker CLI，可以设置别名：

```powershell
# 在 PowerShell 配置文件中添加别名
notepad $PROFILE

# 添加以下内容：
Set-Alias docker podman
Set-Alias docker-compose podman-compose

# 保存后重新加载
. $PROFILE
```

这样可以直接使用 `docker` 和 `docker-compose` 命令。

## 快速开始

### 三步部署

**在 PowerShell 中（推荐）：**
```powershell
# 1. 构建镜像
.\docker.bat build

# 2. 启动容器
.\docker.bat start

# 3. 访问应用
# 浏览器打开: https://localhost:8501
```

**在 CMD 中：**
```cmd
# 1. 构建镜像
docker.bat build

# 2. 启动容器
docker.bat start

# 3. 访问应用
# 浏览器打开: https://localhost:8501
```

> **注意**：
> - PowerShell 中必须使用 `.\docker.bat`，CMD 中可直接使用 `docker.bat`
> - 脚本会自动检测并使用 Podman（兼容 Docker 命令）
> - 容器配置了自动重启策略，系统重启后会自动恢复服务

## 命令说明

### Windows 批处理脚本（推荐）

```cmd
# CMD 中使用
docker.bat build   # 构建容器镜像
docker.bat start   # 启动容器
docker.bat stop    # 停止容器
docker.bat logs    # 查看实时日志
docker.bat export  # 导出镜像（离线部署用）

# PowerShell 中使用（注意前面的 .\）
.\docker.bat build
.\docker.bat start
.\docker.bat stop
.\docker.bat logs
.\docker.bat export
```

### Compose 命令

脚本内部使用 `docker-compose` 命令，Podman 会自动识别。如果需要手动执行：

```bash
# 使用 podman-compose（原生）
podman-compose up -d --build
podman-compose ps
podman-compose logs -f
podman-compose restart
podman-compose down

# 或使用 docker-compose 别名（如果已配置）
docker-compose up -d --build
docker-compose ps
docker-compose logs -f
docker-compose restart
docker-compose down
```

### 原生 Podman 命令

```bash
# 构建镜像
podman build -t image_reviewer:latest .

# 运行容器（兼容 Windows 和 WSL2）
podman run -d --name image_reviewer -p 8501:8501 -v ./certs:/app/certs:Z -v ./data:/data:Z -e TZ=Asia/Shanghai -e ROOT_DIRECTORY=/data --restart always image_reviewer:latest

# 查看日志
podman logs -f image_reviewer

# 停止容器
podman stop image_reviewer

# 删除容器
podman rm image_reviewer

# 如果配置了别名，也可以使用 docker 命令
docker build -t image_reviewer:latest .
docker run -d --name image_reviewer -p 8501:8501 \
  -v ./certs:/app/certs:Z -v ./data:/data:Z \
  -e TZ=Asia/Shanghai -e ROOT_DIRECTORY=/data \
  --restart always image_reviewer:latest
```

> **注意**：`:Z` 选项确保 SELinux 兼容性（WSL2 环境）

## 离线部署

### 1. 导出镜像

在联网机器上：

```bash
# 使用脚本导出（推荐）
.\docker.bat export

# 或使用 Podman 命令
podman save -o image_reviewer.tar image_reviewer:latest

# 或使用 Docker 别名
docker save -o image_reviewer.tar image_reviewer:latest
```

### 2. 传输文件

将以下文件复制到目标机器：
- `image_reviewer.tar` - 镜像文件
- `docker-compose.yml` - 配置文件
- `docker.bat` - 管理脚本
- `certs/` - 证书目录（可选）
- `data/` - 数据目录（可选）

### 3. 导入镜像

在目标机器上（确保已安装 Podman Desktop）：

```bash
# 使用 Podman
podman load -i image_reviewer.tar

# 或使用 Docker 别名
docker load -i image_reviewer.tar
```

### 4. 启动容器

```bash
# 使用脚本
.\docker.bat start

# 或使用 compose
podman-compose up -d
# 或
docker-compose up -d
```

## 数据持久化

以下目录会被挂载到宿主机，数据持久保存：

| 容器路径 | 宿主机路径 | 说明 |
|---------|----------|------|
| `/app/certs` | `./certs` | SSL 证书 |
| `/data` | `./data` | 应用数据（图片、日志、数据库） |

### 数据备份

```bash
# Windows
tar -czf backup_%date:~0,4%%date:~5,2%%date:~8,2%.tar.gz data/

# Linux
tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

## 配置说明

### 端口配置

默认端口：`8501`

修改方法：
1. 编辑 `config.json` 中的 `port` 值
2. 编辑 `docker-compose.yml` 中的端口映射
3. 重新构建并启动

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TZ` | 时区 | Asia/Shanghai |
| `ROOT_DIRECTORY` | 数据根目录 | /data |

### 自定义数据目录

编辑 `docker-compose.yml`：

```yaml
volumes:
  - ./certs:/app/certs
  - /your/custom/path:/data  # 修改此处
```

## 常见问题

### 0. 容器引擎问题

#### Podman Desktop 未安装

**错误**：`podman: command not found` 或 `docker: command not found`

**解决**：
1. 下载并安装 Podman Desktop：https://podman-desktop.io/downloads
2. 启动 Podman Desktop，等待初始化完成
3. 重启终端，再次尝试

#### Podman Machine 未启动

**错误**：`Cannot connect to Podman. Please verify...`

**解决**：
1. 打开 Podman Desktop
2. 检查 Podman Machine 状态
3. 如果未运行，点击 "Start" 启动
4. 等待启动完成后重试

### 0.5. 网络问题（无法拉取镜像）

**错误**：`failed to resolve source metadata for docker.io/library/python:3.12-slim`

**原因**：无法连接到容器镜像仓库或网络不稳定

**解决方法**：

**方法一：配置 Podman 镜像源（推荐）**

编辑 Podman 配置文件（WSL2 环境中）：

```bash
# 在 WSL2 中编辑配置
wsl -d podman-machine-default

# 编辑 registries.conf
sudo nano /etc/containers/registries.conf

# 添加以下内容：
[[registry]]
location = "docker.io"
[[registry.mirror]]
location = "docker.m.daocloud.io"
[[registry.mirror]]
location = "dockerproxy.com"
```

或在 Podman Desktop 中配置镜像源。

**方法二：使用代理**

```powershell
# PowerShell 中设置代理
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"

# 然后构建
.\docker.bat build
```

**方法三：使用已下载的镜像**

如果有离线镜像文件 `image_reviewer.tar`：

```powershell
podman load -i image_reviewer.tar
# 或
docker load -i image_reviewer.tar

# 然后启动
.\docker.bat start
```

### 1. PowerShell 无法识别脚本命令

**错误**：`无法将"docker.bat"项识别为 cmdlet、函数、脚本文件...`

**解决**：在 PowerShell 中必须使用 `.\docker.bat` 而不是 `docker.bat`

```powershell
# 错误
docker.bat build

# 正确
.\docker.bat build
```

或者切换到 CMD 运行：

```cmd
cmd /c docker.bat build
```

### 2. 端口被占用

**错误**：`Bind for 0.0.0.0:8501 failed: port is already allocated`

**解决**：
```bash
# 查看端口占用
netstat -ano | findstr 8501

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8502:8501"  # 改用 8502 端口
```

### 3. 容器无法启动

**解决步骤**：
```powershell
# 1. 查看日志
.\docker.bat logs

# 2. 检查 Podman 状态
podman ps -a
# 或使用别名
docker ps -a

# 3. 检查镜像是否存在
podman images | findstr image_reviewer
# 或
docker images | findstr image_reviewer

# 4. 检查 Podman Machine 状态
podman machine list

# 5. 重新构建
.\docker.bat build
```

### 4. 证书警告

首次访问 HTTPS 时，浏览器会提示"证书不受信任"，这是正常的（自签名证书）。

**解决**：点击"高级" → "继续访问"

如需重新生成证书：
```bash
# 删除旧证书
rm -rf certs/*

# 重启容器（会自动生成新证书）
docker-compose restart
```

### 5. 无法访问应用

**检查清单**：
- [ ] 容器是否运行：`podman-compose ps` 或 `docker-compose ps`
- [ ] 端口是否正确：`podman-compose logs | findstr "Running"`
- [ ] Podman Machine 是否运行：`podman machine list`
- [ ] 防火墙是否允许：`netsh advfirewall firewall show rule name=all | findstr 8501`
- [ ] 端口映射是否正确：`podman port image_reviewer`
- [ ] 尝试使用 `http://127.0.0.1:8501` 访问

**WSL2 端口转发问题**：

如果 WSL2 端口无法访问，手动配置端口转发：

```powershell
# 以管理员身份运行 PowerShell
netsh interface portproxy add v4tov4 listenport=8501 listenaddress=0.0.0.0 connectport=8501 connectaddress=$(wsl hostname -I)
```

## 运维操作

### 查看容器信息

```bash
# 容器状态
podman-compose ps
# 或
docker-compose ps

# 资源占用
podman stats image_reviewer
# 或
docker stats image_reviewer

# 容器详情
podman inspect image_reviewer

# 进入容器
podman exec -it image_reviewer /bin/bash
# 或
docker-compose exec image-reviewer /bin/bash
```

### Podman Machine 管理

```bash
# 查看 Machine 状态
podman machine list

# 启动 Machine
podman machine start

# 停止 Machine
podman machine stop

# 重启 Machine
podman machine restart

# 查看 Machine 信息
podman machine inspect
```

### 日志管理

```bash
# 实时查看
.\docker.bat logs

# 或使用 compose
podman-compose logs -f
docker-compose logs -f

# 最近 100 行
podman-compose logs --tail=100

# 指定时间范围
podman-compose logs --since "2024-01-01T00:00:00"

# 容器日志（原生命令）
podman logs -f image_reviewer
```

### 更新应用

```powershell
# 方式一：使用脚本（推荐）
.\docker.bat stop
.\docker.bat build
.\docker.bat start

# 方式二：使用 compose
podman-compose down
podman-compose up -d --build

# 或使用别名
docker-compose down
docker-compose up -d --build
```

### 清理资源

```bash
# 停止并删除容器
podman-compose down
# 或
docker-compose down

# 删除镜像
podman rmi image_reviewer:latest

# 清理悬空镜像
podman image prune -f

# 清理所有未使用资源
podman system prune -a

# 重置 Podman（完全清理）
podman system reset
```

## 性能优化

### 限制容器资源

编辑 `docker-compose.yml`：

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

### 日志轮转

编辑 `docker-compose.yml`：

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

## 安全建议

1. **使用正式证书**：生产环境替换自签名证书为正式 SSL 证书
2. **定期备份**：设置定时任务备份 `data` 目录
3. **限制访问**：配置防火墙规则，限制访问来源
4. **及时更新**：定期更新基础镜像和依赖包
5. **监控日志**：定期检查应用日志，及时发现异常
6. **Rootless 模式**：Podman 默认以非特权模式运行，更安全
7. **自动重启**：已配置 `--restart=always`，确保服务高可用

## 故障排查

### 查看完整日志

```bash
# 容器日志
docker logs image_reviewer > container.log

# Docker Compose 日志
docker-compose logs > compose.log

# 应用日志（容器内）
docker-compose exec image-reviewer cat /data/logs/app.log
```

### 检查容器健康状态

```bash
# 容器状态
docker-compose ps

# 容器进程
docker-compose top

# 容器资源
docker stats image_reviewer --no-stream
```

### 网络诊断

```bash
# 检查端口监听
docker-compose exec image-reviewer netstat -tlnp

# 测试端口连通性
telnet localhost 8501

# 检查容器网络
docker network inspect image-reviewer-network
```

## Podman 与 Docker 差异

### 主要优势
- **无守护进程**：Podman 不需要后台守护进程（dockerd），更轻量安全
- **Rootless**：默认以非 root 用户运行，提升安全性
- **OCI 兼容**：完全兼容 OCI 标准，与 Docker 镜像格式互通
- **Pod 支持**：原生支持 Kubernetes Pod 概念

### 命令映射

| Docker 命令 | Podman 命令 | 说明 |
|------------|------------|------|
| `docker build` | `podman build` | 构建镜像 |
| `docker run` | `podman run` | 运行容器 |
| `docker ps` | `podman ps` | 查看容器 |
| `docker images` | `podman images` | 查看镜像 |
| `docker-compose` | `podman-compose` | 编排工具 |

### 兼容性说明

- ✅ 本项目完全兼容 Podman
- ✅ 不依赖 Docker 守护进程特性
- ✅ 使用标准 OCI 镜像格式
- ✅ 已配置自动重启策略
- ✅ 兼容 Windows 和 WSL2 文件系统

## 参考资源

- [Podman Desktop 官网](https://podman-desktop.io/)
- [Podman 官方文档](https://docs.podman.io/)
- [Docker 兼容性指南](https://podman.io/getting-started/)
- [项目主文档](README.md)

