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
    # 项目根目录（main.py 所在目录）
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, "backend")

    # 将 backend 目录添加到 Python 搜索路径（确保能找到 config 模块）
    sys.path.insert(0, backend_dir)

    # 在 chdir 之前，将 sys.argv[0] 设为绝对路径（Django autoreloader 需要）
    sys.argv[0] = os.path.abspath(__file__)

    # 切换到 backend 目录
    os.chdir(backend_dir)

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
