"""工具函数：验证码/编辑码/邮件发送"""
import random
import string
import os
import logging
import socket
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import EmailMessage
from django.conf import settings
from .redis_service import VerificationCodeService

logger = logging.getLogger(__name__)


def generate_verification_code(length=6):
    """生成 N 位纯数字验证码"""
    return ''.join(random.choices(string.digits, k=length))


def save_verification_code(email, code):
    """保存验证码到 Redis（5分钟过期）
    
    Args:
        email: 用户邮箱
        code: 验证码
        
    Returns:
        tuple: (success: bool, message: str)
    """
    return VerificationCodeService.save_code(email, code)


def verify_verification_code(email, code):
    """验证验证码
    
    Args:
        email: 用户邮箱
        code: 用户输入的验证码
        
    Returns:
        tuple: (success: bool, message: str)
    """
    return VerificationCodeService.verify_code(email, code)


def test_smtp_connection():
    """测试 SMTP 服务器连接
    
    Returns:
        tuple: (success: bool, message: str)
    """
    host = settings.EMAIL_HOST
    port = settings.EMAIL_PORT
    timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
    
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, f'SMTP 服务器 {host}:{port} 连接成功'
        else:
            return False, f'无法连接到 SMTP 服务器 {host}:{port}（错误码: {result}）'
    except socket.timeout:
        return False, f'连接 SMTP 服务器超时（{timeout}秒）'
    except Exception as e:
        return False, f'连接测试失败: {str(e)}'


def send_verification_email(to_email, code):
    """发送验证码邮件
    
    Returns:
        tuple: (success: bool, message: str)
    """
    subject = '同窗录 - 邮箱验证码'
    message = f"""
您好！

您的同窗录注册验证码为：{code}

该验证码有效期为 5 分钟，请尽快完成注册。
如非本人操作，请忽略此邮件。

—— 同窗录团队
"""
    
    # 开发模式下使用 console backend，直接在控制台输出验证码
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        logger.info(f'[开发模式] 验证码已生成: 邮箱={to_email}, 验证码={code}')
        logger.info(f'[开发模式] 请在控制台查看验证码')
        return True, f'验证码已生成（开发模式）：{code}'
    
    # 先测试 SMTP 连接
    host = settings.EMAIL_HOST
    port = settings.EMAIL_PORT
    timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
    
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            logger.error(f'SMTP 服务器连接失败: {host}:{port}, 错误码: {result}')
            return False, f'无法连接到邮件服务器 {host}:{port}，请检查网络或SMTP配置'
    except socket.timeout:
        logger.error(f'SMTP 服务器连接超时: {host}:{port}')
        return False, f'连接邮件服务器超时（{timeout}秒），请检查网络'
    except Exception as e:
        logger.error(f'SMTP 连接测试异常: {str(e)}')
        return False, f'邮件服务器连接测试失败: {str(e)}'
    
    # 使用配置的超时发送邮件
    try:
        email_msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        
        backend = EmailBackend(
            host=host,
            port=port,
            use_ssl=settings.EMAIL_USE_SSL,
            use_tls=getattr(settings, 'EMAIL_USE_TLS', False),
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            timeout=timeout,
        )
        backend.open()
        backend.send_messages([email_msg])
        backend.close()
        
        logger.info(f'验证码邮件发送成功: {to_email}')
        return True, '验证码已发送，请查收邮件'
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        logger.error(f'邮件发送失败: 类型={error_type}, 接收人={to_email}, 错误={error_msg}')
        
        # 根据错误类型给出友好提示
        if 'Connection refused' in error_msg or 'connection' in error_msg.lower():
            return False, '邮件服务器连接失败，请检查SMTP配置'
        elif 'Authentication failed' in error_msg or 'auth' in error_msg.lower() or '535' in error_msg:
            return False, '邮箱认证失败，请检查账号和授权码是否正确'
        elif 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
            return False, '邮件服务器连接超时，请稍后重试'
        elif 'User not local' in error_msg or '550' in error_msg or '554' in error_msg:
            return False, '收件人地址无效或被服务器拒绝'
        else:
            return False, f'邮件发送失败：{error_msg}'


def delete_media_files(media_files):
    """删除媒体文件记录及磁盘文件"""
    for media in media_files:
        if media.file and os.path.isfile(media.file.path):
            os.remove(media.file.path)
    media_files.delete()
