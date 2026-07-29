# 🌸 同窗录 · Classmates Record

> 珍藏每一份同窗情谊

一款基于 Django 5.0 构建的同学录系统，帮助你轻松收集同学们的联系方式和珍贵回忆。

## ✨ 功能特点

- 📝 **无需注册填写** — 把分享链接发给同学，点开就能填，零门槛参与
- 📸 **照片视频全支持** — 支持上传多张照片和视频，记录大家现在的样子
- 🔍 **快速搜索查找** — 按名字一键搜索，快速找到老同学
- 🔄 **回收站机制** — 软删除 + 10天可还原，永久删除需二次确认
- 🌐 **语义化 URL** — 基于同学录名称和姓名的友好链接结构
- 📱 **响应式设计** — 移动端和桌面端完美适配

## 🛠 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Django 5.0+ |
| 数据库 | PostgreSQL 16 |
| Python | 3.12 |
| 部署 | Docker + Gunicorn |
| 环境配置 | python-dotenv |

## 📁 项目结构

```
classmates/
├── backend/
│   ├── config/              # Django 项目配置
│   │   ├── settings.py      # 应用设置
│   │   ├── urls.py          # 根 URL 路由
│   │   ├── wsgi.py          # WSGI 入口
│   │   └── asgi.py          # ASGI 入口
│   ├── core/                # 核心业务应用
│   │   ├── migrations/      # 数据库迁移文件
│   │   ├── templates/core/  # HTML 模板
│   │   ├── static/core/     # 静态资源（CSS、上传文件）
│   │   ├── models.py        # 数据模型
│   │   ├── views.py         # 视图函数
│   │   ├── urls.py          # URL 路由
│   │   └── utils.py         # 工具函数
│   └── manage.py            # Django 管理脚本
├── deploy/
│   └── Dockerfile           # Docker 镜像构建文件
├── docs/                    # 项目文档
├── docker-compose.yml       # Docker Compose 配置
├── .env.example             # 环境变量模板
├── main.py                  # 项目入口（开发服务器）
└── requirements.txt         # Python 依赖
```

## 🚀 快速开始

### 前提条件

- Python 3.12+
- PostgreSQL 14+
- pip

### 本地开发

**1. 克隆项目**

```bash
git clone https://github.com/class-23/classmates.git
cdcd classmates
```

**2. 创建虚拟环境并安装依赖**

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**3. 配置环境变量**

```bash
# Windows PowerShell
Copy-Item .env.example .env
```

编辑 `.env` 文件，修改以下关键配置：

```bash
# 数据库配置
DB_NAME=classmates_record
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=5432

# 邮箱配置（用于发送注册验证码）
EMAIL_HOST=smtp.qq.com
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-auth-code
```

**4. 数据库迁移**

```bash
cd backend
python manage.py migrate
```

**5. 创建管理员账户（可选）**

```bash
python manage.py createsuperuser
```

**6. 启动开发服务器**

```bash
# 方式一：使用项目入口
cd classmates
python main.py

# 方式二：直接使用 Django
cd backend
python manage.py runserver 0.0.0.0:2323
```

服务器启动后访问 [http://localhost:2323](http://localhost:2323) 即可。

## 🐳 Docker 部署

### 1. 准备工作

确保服务器已安装：
- Docker 24.0+
- Docker Compose v2

### 2. 配置环境变量

```bash
# 复制模板
cp .env.example .env

# 修改关键配置
# - DB_PASSWORD: 设置安全的数据库密码
# - DJANGO_SECRET_KEY: 设置随机密钥
# - DJANGO_DEBUG: 生产环境设为 false
# - DJANGO_ALLOWED_HOSTS: 指定实际域名（不要使用 *）
```

### 3. 一键启动

```bash
# 构建并启动所有服务
docker compose up -d --build
```

### 4. 查看服务状态

```bash
docker compose ps
docker compose logs -f web
```

### 5. 常用命令

```bash
# 停止服务
docker compose down

# 重启服务
docker compose restart

# 重新构建并启动
docker compose up -d --build

# 查看数据库容器日志
docker compose logs -f db

# 进入 Web 容器
docker compose exec web bash

# 执行数据库迁移
docker compose exec web python manage.py migrate

# 收集静态文件
docker compose exec web python manage.py collectstatic --noinput
```

### 6. 数据持久化

Docker 卷自动持久化以下数据：
- `pgdata`: PostgreSQL 数据库数据
- `media_data`: 用户上传的媒体文件
- `static_data`: Django 静态文件

### 7. 生产环境安全清单

- [ ] 修改 `DJANGO_SECRET_KEY` 为随机密钥
- [ ] 设置 `DJANGO_DEBUG=false`
- [ ] 指定 `DJANGO_ALLOWED_HOSTS` 为实际域名
- [ ] 设置安全的 `DB_PASSWORD`
- [ ] 配置 HTTPS 反向代理（Nginx/Caddy）
- [ ] 启用防火墙，仅开放必要端口
- [ ] 定期备份数据库和媒体文件

## 📖 使用指南

### 1. 注册与登录

1. 访问首页，点击「免费创建同学录」
2. 使用邮箱注册，需通过邮箱验证码验证
3. 登录后自动进入仪表盘

### 2. 创建同学录

1. 在仪表盘点击「新建同学录」
2. 输入同学录名称（如：447班）
3. 创建成功后进入同学录详情页

### 3. 分享与收集信息

1. 在同学录详情页点击「📋 复制分享链接」
2. 将链接发送给同学
3. 同学打开链接填写信息并提交
4. 无需注册即可填写，降低参与门槛

### 4. 管理同学信息

- 查看同学详情页，了解联系方式和回忆
- 使用搜索功能快速定位同学
- 删除操作进入回收站，10天内可还原

## 🔐 安全说明

- 注册流程采用邮箱验证码验证
- 用户密码使用 Django PBKDF2 加密存储
- 会话有效期默认为 7 天
- 生产环境强制 HTTPS 传输
- CSRF 保护已启用

## ⚙️ 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DJANGO_SECRET_KEY` | 安全密钥 | 需自定义 |
| `DJANGO_DEBUG` | 调试模式 | `true` |
| `DJANGO_ALLOWED_HOSTS` | 允许的主机 | `*` |
| `DJANGO_RUN_PORT` | 开发服务器端口 | `2323` |
| `DB_NAME` | 数据库名称 | `classmates_record` |
| `DB_USER` | 数据库用户 | `root` |
| `DB_PASSWORD` | 数据库密码 | - |
| `DB_HOST` | 数据库主机 | `127.0.0.1` |
| `DB_PORT` | 数据库端口 | `5432` |
| `EMAIL_HOST` | SMTP 服务器 | `smtp.qq.com` |
| `EMAIL_HOST_USER` | 发件邮箱 | - |
| `EMAIL_HOST_PASSWORD` | 邮箱授权码 | - |
| `SESSION_COOKIE_AGE` | 会话有效期（秒） | `604800` |

## 📝 开发命令

```bash
# 创建迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 查看 SQL 语句
python manage.py sqlmigrate core 0001

# 进入 Django Shell
python manage.py shell

# 收集静态文件（生产部署）
python manage.py collectstatic --noinput
```

## 🗺️ URL 路由结构

### 公开路由

| 路径 | 说明 |
|------|------|
| `/` | 首页 |
| `/register/` | 注册 |
| `/login/` | 登录 |
| `/logout/` | 退出 |
| `/join/<uuid>/` | 填写同学录表单 |
| `/join/<uuid>/success/` | 填写成功页 |
| `/edit/<code>/` | 编辑已提交信息 |

### 需要登录的路由

| 路径 | 说明 |
|------|------|
| `/dashboard/` | 我的同学录列表 |
| `/notebook/create/` | 创建同学录 |
| `/notebook/<slug>/` | 同学录详情页 |
| `/notebook/<slug>/trash/` | 回收站 |
| `/notebook/<slug>/<name>/` | 同学详情页 |

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

## 🙏 致谢

感谢每一位为这个项目贡献代码的同学！

---

Made with ❤️ for preserving precious friendship and memories.