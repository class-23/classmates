#!/bin/bash
set -e

echo "=========================================="
echo " 同窗录 - 容器启动脚本"
echo "=========================================="

cd /app/backend

# ===== 1. 等待数据库就绪 =====
echo ""
echo "[1/3] 等待数据库就绪..."
until python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>/dev/null; do
    echo "  ⏳ 数据库尚未就绪，等待 2 秒..."
    sleep 2
done
echo "  ✅ 数据库已就绪"

# ===== 2. 执行数据库迁移 =====
echo ""
echo "[2/3] 执行数据库迁移..."
python manage.py migrate --noinput
echo "  ✅ 数据库迁移完成"

# ===== 3. 收集静态文件 =====
echo ""
echo "[3/3] 收集静态文件..."
python manage.py collectstatic --noinput
echo "  ✅ 静态文件收集完成"

# ===== 4. 创建必要目录 =====
mkdir -p /app/backend/media
mkdir -p /app/backend/staticfiles

echo ""
echo "=========================================="
echo " 🚀 启动 Gunicorn 服务器"
echo "=========================================="
echo ""

# 启动 Gunicorn（exec 确保信号正确传递）
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${DJANGO_RUN_PORT:-2323} \
    --workers ${GUNICORN_WORKERS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --loglevel ${GUNICORN_LOGLEVEL:-info}