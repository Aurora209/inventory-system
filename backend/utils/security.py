"""安全增强工具"""
import re
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SQLInjectionProtector:
    """SQL注入防护"""
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 255) -> Optional[str]:
        """清理输入字符串"""
        if input_str is None:
            return None
        
        # 移除首尾空格
        cleaned = input_str.strip()
        
        # 限制长度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
            logger.warning("输入字符串被截断: 原长度=%s, 截断后=%s", len(input_str), max_length)
        
        # 移除潜在的SQL注入字符
        dangerous_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC)\b)",
            r"(\-\-|\#|\/\*)",
            r"(\b(OR|AND)\b.*=)",
            r"(;\s*$)"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                logger.warning("检测到潜在的SQL注入尝试: %s", cleaned)
                raise ValueError("输入包含不安全的字符")
        
        return cleaned
    
    @staticmethod
    def validate_table_name(table_name: str) -> bool:
        """验证表名是否安全"""
        if not table_name or not isinstance(table_name, str):
            return False
        
        # 只允许字母、数字和下划线
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            return False
        
        # 黑名单检查
        blacklist = ['sqlite_master', 'sqlite_sequence', 'admin', 'system']
        if table_name.lower() in blacklist:
            return False
        
        return True
    
    @staticmethod
    def validate_column_name(column_name: str) -> bool:
        """验证列名是否安全"""
        return SQLInjectionProtector.validate_table_name(column_name)

class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号格式"""
        if not phone:
            return False
        
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
        """验证文件扩展名"""
        if not filename:
            return False
        
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

class RateLimiter:
    """简单的速率限制器"""
    
    _requests = {}
    
    @staticmethod
    def is_rate_limited(identifier: str, max_requests: int, window_seconds: int) -> bool:
        """检查是否超过速率限制"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        # 清理过期的请求记录
        if identifier in RateLimiter._requests:
            RateLimiter._requests[identifier] = [
                req_time for req_time in RateLimiter._requests[identifier]
                if req_time > window_start
            ]
        
        # 检查当前请求数
        current_requests = RateLimiter._requests.get(identifier, [])
        if len(current_requests) >= max_requests:
            return True
        
        # 记录当前请求
        current_requests.append(now)
        RateLimiter._requests[identifier] = current_requests
        
        return False

def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """速率限制装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 使用函数名和参数作为标识符（实际应用中应该使用IP地址等）
            identifier = f"{func.__module__}.{func.__name__}"
            
            if RateLimiter.is_rate_limited(identifier, max_requests, window_seconds):
                logger.warning("速率限制触发: %s", identifier)
                from utils.api_response import APIResponse
                return APIResponse.error(
                    "请求过于频繁，请稍后重试",
                    code=429,
                    error_code="RATE_LIMITED"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator