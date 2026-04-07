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

## 快速启动

### 第一步：安装依赖

确保你在项目根目录下，然后激活虚拟环境并安装依赖：

```bash
# 创建虚拟环境（如果还未创建）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 第二步：准备测试数据

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

#### YOLO标注文件格式（可选）

如果你有YOLO格式的边界框标注，可以创建与图片同名的`.txt`文件：

```
# 格式：x1 y1 x2 y2 confidence
100.5 200.3 300.7 400.2 0.95
150.0 250.0 350.0 450.0 0.88
```

### 第三步：启动应用

#### HTTPS模式（推荐）

```bash
python run_app.py
```

首次启动会自动生成SSL证书。

#### HTTP模式

```bash
python run_app.py --no-https
```

### 第四步：访问应用

在浏览器中打开：
- HTTPS: `https://localhost:8501`
- HTTP: `http://localhost:8501`

**注意**：使用HTTPS时，浏览器会提示证书不受信任，这是正常的。选择"继续访问"即可。

### 第五步：开始使用

1. 在侧边栏输入你的姓名（可选）
2. 选择项目文件夹
3. 使用键盘快捷键浏览和分类图片

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

## 常见问题

### Q: 如何修改端口？
A: 编辑 `config.json` 文件中的 `port` 字段。

### Q: 如何在局域网中访问？
A: 确保 `config.json` 中的 `host` 设置为 `0.0.0.0`，然后使用服务器的IP地址访问，例如 `https://192.168.1.100:8501`

### Q: 边界框不显示？
A: 确保图片同目录下有对应的 `.txt` 标注文件，并检查格式是否正确。

### Q: 如何清空操作历史？
A: 删除 `data/app.db` 文件，系统会自动重新创建。

### Q: 无法启动应用？
A: 检查端口是否被占用：
```bash
netstat -ano | findstr :8501
```

### Q: SSL证书错误？
A: 删除 `certs` 目录后重新启动，系统会自动生成新证书。

## 测试安装

运行测试脚本验证安装：

```bash
python test_basic.py
```

应该看到 5/6 或 6/6 测试通过。

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

## 项目技术总结

### 核心架构

**架构模式**：
- MVC模式：清晰的代码组织
- RESTful API：标准化的接口设计
- 单例模式：数据库连接管理

**文件结构**：

```
ImageReviewer/
├── 核心模块 (8个)
│   ├── app.py                 (Flask应用主文件)
│   ├── config_handler.py      (配置处理)
│   ├── database.py            (数据库操作)
│   ├── image_handler.py       (图片处理)
│   ├── user_handler.py        (用户管理)
│   ├── generate_cert.py       (证书生成)
│   ├── run_app.py            (启动脚本)
│   └── config.json           (配置文件)
│
├── 前端文件 (7个)
│   ├── templates/
│   │   ├── index.html        (主审查页面)
│   │   ├── history.html      (操作历史)
│   │   └── review.html       (结果确认)
│   ├── static/css/
│   │   └── style.css         (样式文件)
│   └── static/js/
│       ├── main.js           (主页面逻辑)
│       ├── history.js        (历史页面逻辑)
│       └── review.js         (确认页面逻辑)
│
└── 文档与测试
    ├── README.md
    ├── requirements.txt
    └── test_basic.py
```

**代码统计**： 
- Python代码: ~2500行
- JavaScript代码: ~800行
- CSS代码: ~500行
- HTML代码: ~400行
- **总计**: ~4200行

### API接口 (18个)

**基础功能 (6个)**：
- `GET /api/folders` - 获取文件夹列表
- `GET /api/images` - 获取图片列表
- `GET /api/image` - 获取图片数据
- `GET /api/preload` - 预加载图片
- `GET /api/state` - 获取全局状态
- `POST /api/state` - 更新全局状态

**用户管理 (2个)**：
- `GET /api/user` - 获取用户信息
- `POST /api/user/name` - 更新用户名称

**图片分类 (1个)**：
- `POST /api/classify` - 分类图片

**撤回功能 (2个)**：
- `GET /api/undo/available` - 检查撤回可用性
- `POST /api/undo` - 执行撤回

**操作历史 (3个)**：
- `GET /api/operations` - 查询操作记录
- `GET /api/operations/stats` - 获取统计信息
- `GET /api/users` - 获取用户列表

**结果确认 (2个)**：
- `GET /api/review/images` - 获取分类结果列表
- `GET /api/review/image` - 获取分类结果图片

### 数据库设计

**表结构 (3个表)**：

1. **users** - 用户表
   - id, ip, name, first_seen, last_active

2. **operations** - 操作记录表
   - id, user_ip, user_name, operation_type, image_name, source_folder, target_folder, timestamp

3. **undo_history** - 撤回历史表
   - id, user_ip, operation_id, image_name, from_folder, to_folder, txt_file_exists, timestamp

**索引 (3个)**：
- idx_operations_user_ip
- idx_operations_timestamp
- idx_undo_history_user_ip

### 主要优势

1. **性能优化**
   - 图片预加载机制
   - 快速的响应速度
   - 优化的内存占用

2. **用户体验**
   - 完整的键盘快捷键
   - 流畅的交互体验
   - 现代化UI设计

3. **数据管理**
   - 结构化的数据库存储
   - 完整的操作记录
   - 统计分析功能

4. **可维护性**
   - 清晰的代码结构
   - 模块化设计
   - 详细的文档

## 生产环境部署建议

- 建议使用 Gunicorn + Nginx
- 配置SSL证书（使用正式证书）
- 设置合适的并发数
- 配置日志轮转

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

## 依赖管理

* 在虚拟环境下运行下面命令，从本地安装依赖包

```bash
pip install -r requirements.txt --no-index --find-links=./packages
```

### 依赖打包方法

* 生成依赖列表

```bash
pip freeze > requirements.txt
```

* 下载依赖包至本地

```bash
pip download -d ./packages -r requirements.txt
```

