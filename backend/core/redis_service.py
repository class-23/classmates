"""Redis 服务封装 - 用于验证码等临时数据存储"""
import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

# Redis 连接实例
_redis_client = None


def get_redis_client():
    """获取 Redis 客户端单例"""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', '127.0.0.1'),
                port=int(getattr(settings, 'REDIS_PORT', 6379)),
                password=getattr(settings, 'REDIS_PASSWORD', None) or None,
                db=int(getattr(settings, 'REDIS_DB', 0)),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # 测试连接
            _redis_client.ping()
            logger.info('Redis 连接成功')
        except redis.ConnectionError as e:
            logger.warning(f'Redis 连接失败: {e}，将使用内存存储')
            _redis_client = None
        except Exception as e:
            logger.warning(f'Redis 初始化异常: {e}')
            _redis_client = None
    return _redis_client


class VerificationCodeService:
    """验证码服务 - 使用 Redis 存储"""
    
    # Key 前缀
    PREFIX = 'verification_code:'
    # 过期时间（秒）- 5分钟
    EXPIRE_SECONDS = 300
    # 发送间隔（秒）- 60秒
    SEND_INTERVAL = 60
    # 固定测试验证码（开发用）
    TEST_CODE = '888888'
    
    @classmethod
    def _make_key(cls, email):
        """生成 Redis Key"""
        return f'{cls.PREFIX}{email.strip().lower()}'
    
    @classmethod
    def save_code(cls, email, code):
        """保存验证码到 Redis
        
        Args:
            email: 用户邮箱
            code: 验证码
            
        Returns:
            tuple: (success: bool, message: str)
        """
        client = get_redis_client()
        key = cls._make_key(email)
        
        if client is None:
            # Redis 不可用时，使用简单的内存存储（仅开发用）
            return cls._save_in_memory(email, code)
        
        try:
            # 检查发送间隔
            ttl = client.ttl(key)
            if ttl is not None and ttl > cls.EXPIRE_SECONDS - cls.SEND_INTERVAL:
                # 距上次发送不到 60 秒
                remaining = cls.EXPIRE_SECONDS - ttl
                if remaining > cls.SEND_INTERVAL:
                    wait_time = remaining - cls.SEND_INTERVAL
                    return False, f'请 {int(wait_time)} 秒后再试'
            
            # 存储验证码，设置 5 分钟过期
            pipe = client.pipeline()
            pipe.setex(key, cls.EXPIRE_SECONDS, code)
            pipe.execute()
            
            logger.info(f'验证码已保存到 Redis: email={email}, ttl={cls.EXPIRE_SECONDS}s')
            return True, '验证码已发送'
        except Exception as e:
            logger.error(f'Redis 保存验证码失败: {e}')
            return cls._save_in_memory(email, code)
    
    @classmethod
    def verify_code(cls, email, code):
        """验证验证码
        
        Args:
            email: 用户邮箱
            code: 用户输入的验证码
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # 固定测试验证码（开发用）
        if code == cls.TEST_CODE:
            logger.info(f'使用测试验证码验证成功: email={email}')
            return True, '验证码正确'
        
        client = get_redis_client()
        key = cls._make_key(email)
        
        if client is None:
            return cls._verify_from_memory(email, code)
        
        try:
            stored_code = client.get(key)
            
            if stored_code is None:
                return False, '验证码已过期或不存在'
            
            if stored_code != code:
                return False, '验证码不正确'
            
            # 验证成功后立即删除验证码（一次性使用）
            client.delete(key)
            
            logger.info(f'验证码验证成功: email={email}')
            return True, '验证码正确'
        except Exception as e:
            logger.error(f'Redis 验证验证码失败: {e}')
            return cls._verify_from_memory(email, code)
    
    @classmethod
    def get_remaining_time(cls, email):
        """获取验证码剩余有效时间（秒）
        
        Args:
            email: 用户邮箱
            
        Returns:
            int: 剩余秒数，-1 表示不存在或已过期
        """
        client = get_redis_client()
        key = cls._make_key(email)
        
        if client is None:
            return -1
        
        try:
            ttl = client.ttl(key)
            return ttl if ttl and ttl > 0 else -1
        except Exception:
            return -1
    
    # ========= 内存存储降级方案 =========
    # 当 Redis 不可用时使用（仅用于开发/测试）
    _memory_store = {}
    
    @classmethod
    def _save_in_memory(cls, email, code):
        """内存存储（降级方案）"""
        import time
        key = email.strip().lower()
        cls._memory_store[key] = {
            'code': code,
            'expire_at': time.time() + cls.EXPIRE_SECONDS
        }
        logger.warning(f'使用内存存储验证码: email={email}')
        return True, '验证码已发送（内存存储模式）'
    
    @classmethod
    def _verify_from_memory(cls, email, code):
        """内存验证（降级方案）"""
        import time
        key = email.strip().lower()
        data = cls._memory_store.get(key)
        
        if not data:
            return False, '验证码已过期或不存在'
        
        if time.time() > data['expire_at']:
            # 已过期
            del cls._memory_store[key]
            return False, '验证码已过期'
        
        if data['code'] != code:
            return False, '验证码不正确'
        
        # 验证成功后删除
        del cls._memory_store[key]
        return True, '验证码正确'
    
    @classmethod
    def cleanup_expired(cls):
        """清理过期的内存存储数据（可选调用）"""
        import time
        now = time.time()
        expired_keys = [k for k, v in cls._memory_store.items() if now > v['expire_at']]
        for k in expired_keys:
            del cls._memory_store[k]
        return len(expired_keys)
