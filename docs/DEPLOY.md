# 同学录 - 部署说明

## 方式一：Docker（推荐）

```bash
# 1. 解压
tar xzf classmates-book.tar.gz
cd classmates-book

# 2. 启动
docker compose up -d --build

# 3. 迁移数据库
docker exec classmates-web python manage.py migrate

# 4. 访问
http://localhost:8000/
```

## 方式二：非 Docker

```bash
# 1. 解压
tar xzf classmates-book.tar.gz
cd classmates-book

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 PostgreSQL
#    - 确保 PostgreSQL 已安装并运行
#    - 创建数据库：createdb classmates_record
#    - 创建用户并授权，或直接用现有账号

# 4. 修改数据库配置
#    编辑 backend/config/settings.py
#    找到 DATABASES 配置，填上你的数据库连接信息

# 5. 迁移并启动
cd backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# 或从项目根目录
python main.py
```

## 邮箱配置

如果需要注册功能，配置 QQ 邮箱 SMTP：
```
backend/config/settings.py 中：
EMAIL_HOST_PASSWORD = '你的QQ邮箱授权码'
```

## 默认测试账号

- 邮箱: 731149486@qq.com
- 密码: qq12345678
