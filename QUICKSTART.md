# 快速启动指南

## 第一步：安装依赖

确保你在项目根目录下，然后激活虚拟环境并安装依赖：

```bash
# 激活虚拟环境（如果还未激活）
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 第二步：准备测试数据

在 `data/images` 目录下创建项目文件夹，例如：

```
data/images/
└── test_project/
    ├── image1.jpg
    ├── image1.txt  (可选，YOLO标注文件)
    ├── image2.jpg
    └── ...
```

系统会自动为每个项目创建 `OK` 和 `NOK` 子文件夹。

### YOLO标注文件格式（可选）

如果你有YOLO格式的边界框标注，可以创建与图片同名的`.txt`文件：

```
# 格式：x1 y1 x2 y2 confidence
100.5 200.3 300.7 400.2 0.95
150.0 250.0 350.0 450.0 0.88
```

## 第三步：启动应用

### HTTPS模式（推荐）

```bash
python run_app.py
```

首次启动会自动生成SSL证书。

### HTTP模式

```bash
python run_app.py --no-https
```

## 第四步：访问应用

在浏览器中打开：
- HTTPS: `https://localhost:8501`
- HTTP: `http://localhost:8501`

**注意**：使用HTTPS时，浏览器会提示证书不受信任，这是正常的。选择"继续访问"即可。

## 第五步：开始使用

1. 在侧边栏输入你的姓名（可选）
2. 选择项目文件夹
3. 使用键盘快捷键浏览和分类图片：
   - `←/→` - 上一张/下一张
   - `1` 或 `Enter` - 标记为OK
   - `2` 或 `Space` - 标记为NOK
   - `U` 或 `Ctrl+Z` - 撤回操作
   - `R` - 旋转图片
   - `B` - 显示/隐藏边界框

## 常见问题

### Q: 如何修改端口？
A: 编辑 `config.json` 文件中的 `port` 字段。

### Q: 如何在局域网中访问？
A: 确保 `config.json` 中的 `host` 设置为 `0.0.0.0`，然后使用服务器的IP地址访问，例如 `https://192.168.1.100:8501`

### Q: 边界框不显示？
A: 确保图片同目录下有对应的 `.txt` 标注文件，并检查格式是否正确。

### Q: 如何清空操作历史？
A: 删除 `data/app.db` 文件，系统会自动重新创建。

## 测试安装

运行测试脚本验证安装：

```bash
python test_basic.py
```

应该看到 5/6 或 6/6 测试通过。

## 下一步

- 查看 `README.md` 了解完整功能
- 查看操作历史页面：`/history`
- 查看结果确认页面：`/review`

祝使用愉快！🎉

