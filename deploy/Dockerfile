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

# 收集静态文件
RUN python backend/manage.py collectstatic --noinput --settings=config.settings 2>/dev/null || true

# 启动
EXPOSE 2323
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:2323", "--chdir", "backend", "--workers", "4"]
