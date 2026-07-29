"""自定义 PostgreSQL 数据库后端 - 自动重连 + 自动重启 PG"""
from django.db.backends.postgresql import base
from django.db.utils import OperationalError
import time
import subprocess


class DatabaseWrapper(base.DatabaseWrapper):
    """在标准 PostgreSQL 后端基础上增加自动重连和 PG 重启功能"""

    def get_new_connection(self, conn_params):
        try:
            return super().get_new_connection(conn_params)
        except OperationalError as e:
            if 'Connection refused' in str(e) or 'could not connect' in str(e):
                print("[DB] PostgreSQL 未运行，尝试重启...")
                self._restart_postgresql()
                time.sleep(4)
                return super().get_new_connection(conn_params)
            raise

    def _restart_postgresql(self):
        """通过 Shizuku 或 am 命令重启 Termux 的 PostgreSQL"""
        try:
            subprocess.run(
                ['android-shizuku-cli', 'exec',
                 'am force-stop com.termux'],
                capture_output=True, timeout=5
            )
            time.sleep(2)
            subprocess.run(
                ['android-shizuku-cli', 'exec',
                 'am start -n com.termux/.app.TermuxActivity'],
                capture_output=True, timeout=5
            )
        except Exception as e:
            print(f"[DB] 重启 PostgreSQL 失败: {e}")
