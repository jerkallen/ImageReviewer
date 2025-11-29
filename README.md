# 图片审查系统 (Flask版本)

基于Flask框架的图片审查分类系统，用于工厂产线的视觉检测结果二次确认。

## 功能特点

### 核心功能
- ✅ 图片浏览与导航（上一张/下一张/首页/末页）
- ✅ 支持显示YOLO格式的边界框和置信度
- ✅ 图片旋转功能（90度）
- ✅ 图片分类（OK/NOK文件夹）
- ✅ 撤回功能（最多3步）
- ✅ 图片预加载（提升浏览速度）
- ✅ 多用户支持（基于IP识别）
- ✅ 操作历史记录（SQLite数据库）
- ✅ 操作历史查询页面（支持筛选和导出CSV）
- ✅ 结果确认页面（浏览OK/NOK分类结果）
- ✅ 完整的键盘快捷键支持
- ✅ HTTPS安全连接

### 用户体验
- 🎨 现代化深蓝色主题UI设计
- ⌨️ 丰富的键盘快捷键
- 📱 响应式布局
- 🔄 全局共享浏览状态
- 🚀 图片预加载优化

## 系统要求

- Python 3.8 或更高版本
- Windows / Linux / macOS

## 安装步骤

### 1. 克隆或下载项目

```bash
cd D:\code\projects\ImageReviewer
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
```

激活虚拟环境：
- Windows: `venv\Scripts\activate`
- Linux/macOS: `source venv/bin/activate`

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

编辑 `config.json` 文件来配置系统参数：

```json
{
    "host": "0.0.0.0",          // 服务器地址
    "port": 8501,               // 服务器端口
    "root_directory": "data",   // 数据根目录
    "logs_dir": "logs",         // 日志目录
    "scan_root": "images",      // 图片扫描根目录
    "image_extensions": [".jpg", ".jpeg", ".png", ".bmp"],
    "default_folders": {
        "ok": "OK",             // OK文件夹名称
        "nok": "NOK"            // NOK文件夹名称
    }
}
```

## 目录结构

系统会自动创建以下目录结构：

```
data/
├── images/              # 图片根目录
│   ├── project1/        # 项目文件夹1
│   │   ├── img1.jpg     # 待审查图片
│   │   ├── img1.txt     # YOLO标注文件（可选）
│   │   ├── OK/          # OK分类
│   │   └── NOK/         # NOK分类
│   └── project2/        # 项目文件夹2
│       └── ...
├── app.db               # SQLite数据库
└── logs/                # 日志目录
```

## 启动应用

### 方式一：HTTPS模式启动（推荐）

```bash
python run_app.py
```

首次启动会自动生成自签名SSL证书。

### 方式二：HTTP模式启动

```bash
python run_app.py --no-https
```

### 访问应用

- HTTPS: `https://localhost:8501`
- HTTP: `http://localhost:8501`

**注意**：使用HTTPS时，浏览器会提示证书不受信任（因为是自签名证书），选择"继续访问"即可。

## 使用说明

### 主审查页面

1. **选择项目文件夹**：从侧边栏选择要审查的项目
2. **浏览图片**：使用按钮或键盘快捷键浏览图片
3. **分类操作**：
   - 点击 `OK` 按钮或按 `1/Enter` 标记为合格
   - 点击 `NOK` 按钮或按 `2/Space` 标记为不合格
4. **撤回操作**：点击 `撤回` 按钮或按 `U/Ctrl+Z` 撤回最近的操作

### 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `←` / `A` | 上一张图片 |
| `→` / `D` | 下一张图片 |
| `Home` | 跳转到首张图片 |
| `End` | 跳转到末张图片 |
| `1` / `Enter` | 标记为OK |
| `2` / `Space` | 标记为NOK |
| `U` / `Ctrl+Z` | 撤回操作 |
| `R` | 切换旋转显示 |
| `B` | 切换边界框显示 |

### 操作历史页面

- 查看所有操作记录
- 按日期、用户、操作类型筛选
- 导出CSV文件

### 结果确认页面

- 浏览已分类的图片（OK/NOK文件夹）
- 缩略图网格显示
- 点击查看大图

## 多用户支持

- 系统自动识别用户IP地址
- 用户可以设置显示名称
- 所有操作都会记录用户信息
- 全局共享浏览位置（适合单工位协作）

## 数据库

系统使用SQLite数据库存储：
- 用户信息
- 操作记录
- 撤回历史

数据库文件：`data/app.db`

## 故障排除

### 1. 无法启动应用

检查端口是否被占用：
```bash
netstat -ano | findstr :8501
```

### 2. 图片无法显示

- 检查图片格式是否支持（jpg, jpeg, png, bmp）
- 检查图片路径是否正确
- 查看控制台错误信息

### 3. 边界框不显示

确保图片同目录下有对应的`.txt`标注文件，格式为：
```
x1 y1 x2 y2 confidence
```

### 4. SSL证书错误

删除 `certs` 目录后重新启动，系统会自动生成新证书。

## 开发说明

### 项目结构

```
ImageReviewer/
├── app.py                 # Flask主应用
├── config_handler.py      # 配置处理
├── database.py            # 数据库操作
├── image_handler.py       # 图片处理
├── user_handler.py        # 用户管理
├── generate_cert.py       # 证书生成
├── run_app.py            # 启动脚本
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       ├── history.js
│       └── review.js
└── templates/            # HTML模板
    ├── index.html
    ├── history.html
    └── review.html
```

### API接口

主要API端点：
- `GET /api/folders` - 获取文件夹列表
- `GET /api/images` - 获取图片列表
- `GET /api/image` - 获取图片数据
- `POST /api/classify` - 分类图片
- `POST /api/undo` - 撤回操作
- `GET /api/operations` - 查询操作记录
- `GET /api/operations/stats` - 获取统计信息

## 技术栈

- **后端**: Flask 3.0+
- **数据库**: SQLite 3
- **图片处理**: Pillow 11.0+
- **安全**: pyOpenSSL, cryptography
- **前端**: HTML5, CSS3, JavaScript (原生)

## 许可证

©2024 产线图片二次确认系统 WxP/MOE4

## 更新日志

### v1.0.0 (2024-11-29)
- 初始版本
- 完整的图片审查功能
- 多用户支持
- 操作历史记录
- 撤回功能
- HTTPS支持

