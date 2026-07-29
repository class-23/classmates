#!/usr/bin/env python3
"""同学录 - 项目入口

启动方式（非 Docker）：
    python main.py

启动方式（Docker）：
    docker compose up -d --build
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
load_dotenv(dotenv_path=Path(__file__).resolve().parent / '.env')


def main():
    # 切换到 backend 目录
    os.chdir(os.path.join(os.path.dirname(__file__), "backend"))

    # 默认配置
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    # 从环境变量读取端口，默认 2323
    host = os.getenv('DJANGO_RUN_HOST', '0.0.0.0')
    port = os.getenv('DJANGO_RUN_PORT', '2323')

    # 执行 Django 开发服务器
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver", f"{host}:{port}"])


if __name__ == "__main__":
    main()
