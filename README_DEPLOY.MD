好的，我帮你把上面的部署说明整理成一份**单页精简版 Markdown**，方便直接放在项目里，条理清晰，开箱即用：

---
# 导出镜像
```powershell
podman save -o image_reviewer.tar image_reviewer:latest
```


# ImageReviewer 离线部署指南（Windows + Podman/WSL2）

**目标**：快速部署 `image_reviewer` 镜像并支持开机自启。

---

## 1️⃣ 准备

* 已安装 **Podman Desktop**（WSL2 后端）
* 离线镜像：`image_reviewer.tar`
* 项目结构示例：

```
C:\projects\ImageReviewer\
├─ certs\
├─ data\
└─ image_reviewer.tar
```

---

## 2️⃣ 导入离线镜像

```powershell
podman load -i C:\projects\ImageReviewer\image_reviewer.tar
```

镜像名假设为 `image_reviewer:latest`。

---

## 3️⃣ 启动容器

```powershell
podman run -d --name image_reviewer -p 8501:8501 -v /mnt/c/projects/ImageReviewer/certs:/app/certs -v /mnt/c/projects/ImageReviewer/data:/data -e TZ=Asia/Shanghai -e ROOT_DIRECTORY=/data --restart always image_reviewer:latest

```
```powershell
podman run -d --name image_reviewer --network host -v /mnt/c/projects/ImageReviewer/certs:/app/certs -v /mnt/c/projects/ImageReviewer/data:/data -e TZ=Asia/Shanghai -e ROOT_DIRECTORY=/data --restart always image_reviewer:latest

```



说明：

* `-d`：后台运行
* `-p 8501:8501`：端口映射
* `-v <本地>:<容器>`：挂载卷
* `-e`：环境变量

---

## 4️⃣ 配置开机自启

### 4.1 创建 PowerShell 脚本 `start_image_reviewer.ps1`

```powershell
# === 配置变量 ===
$containerName = 'image_reviewer'

# 等待 180 秒，确保 Podman Desktop / WSL2 启动完成
Start-Sleep -Seconds 180

# 原来的等待 Podman 就绪逻辑
$timeout = 600
$interval = 10
$elapsed = 0
while (-not (Get-Command podman -ErrorAction SilentlyContinue) -and $elapsed -lt $timeout) {
    Start-Sleep -Seconds $interval
    $elapsed += $interval
}

# 如果超时仍找不到 podman，则退出
if (-not (Get-Command podman -ErrorAction SilentlyContinue)) { exit }

# 检查容器是否存在
$containerExists = podman ps -a --filter "name=$containerName" --format '{{.Names}}'

if ($containerExists -eq $containerName) {
    # 如果容器存在但未运行，则启动
    $running = podman ps --filter "name=$containerName" --format '{{.Names}}'
    if ($running -ne $containerName) { podman start $containerName }
}

```

### 4.2 创建任务计划

1. 打开 **任务计划程序** → **创建任务**
2. **触发器**：开机时 / 用户登录时
3. **操作**：

   * 程序/脚本：`powershell.exe`
   * 参数：`-ExecutionPolicy Bypass -File "C:\path\to\start_image_reviewer.ps1"`
4. 勾选“使用最高权限运行”

✅ 完成后，每次开机自动启动容器。

---

## 5️⃣ 验证

```powershell
podman ps          # 查看容器状态
podman logs -f image_reviewer  # 查看实时日志
```

* `Up` 表示容器正常运行

---

## 6️⃣ 注意事项

* 确保端口 `8501` 未被占用
* WSL2 启动慢，可调整 `Start-Sleep` 秒数
* Windows 下卷挂载路径需正确


## 开通防火墙
```powershell
netsh advfirewall firewall add rule name="ImageReviewer Port 8501" dir=in action=allow protocol=TCP localport=8501
---

这份文档简洁明了，直接放到项目根目录即可使用。

---

如果你希望，我可以帮你**再做一个更“极简单页版”**，只保留命令和最核心步骤，方便直接拷贝执行，不看文字说明也能部署。

你希望我做这个吗？
