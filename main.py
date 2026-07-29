#!/usr/bin/env python3
"""同学录 - 项目入口

启动方式（非 Docker）：
    python main.py

启动方式（Docker）：
    docker compose up -d --build
"""

import os
import sys
import subprocess

def main():
    # 切换到 backend 目录
    os.chdir(os.path.join(os.path.dirname(__file__), "backend"))

    # 默认配置
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    # 执行 Django 开发服务器
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver", "0.0.0.0:8000"])

if __name__ == "__main__":
    main()
