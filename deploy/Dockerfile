FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目
COPY . .

# 创建数据目录
RUN mkdir -p /app/backend/media /app/backend/staticfiles

# 设置入口脚本权限
RUN chmod +x deploy/entrypoint.sh

# 暴露端口
EXPOSE 2323

# 使用入口脚本启动
ENTRYPOINT ["deploy/entrypoint.sh"]
