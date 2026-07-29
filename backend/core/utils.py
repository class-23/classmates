"""工具函数：验证码/编辑码/邮件发送"""
import random
import string
import os
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code(length=6):
    """生成 N 位纯数字验证码"""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(to_email, code):
    """发送验证码邮件"""
    subject = '同窗录 - 邮箱验证码'
    message = f"""
您好！

您的同窗录注册验证码为：{code}

该验证码有效期为 5 分钟，请尽快完成注册。
如非本人操作，请忽略此邮件。

—— 同窗录团队
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )


def delete_media_files(media_files):
    """删除媒体文件记录及磁盘文件"""
    for media in media_files:
        if media.file and os.path.isfile(media.file.path):
            os.remove(media.file.path)
    media_files.delete()
