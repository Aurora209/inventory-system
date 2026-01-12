"""性能监控和缓存工具"""
import time
import functools
import logging
from typing import Any, Callable, Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    _instance = None
    _metrics = defaultdict(list)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def record_metric(cls, metric_name: str, value: float, tags: Dict[str, str] = None):
        """记录性能指标"""
        timestamp = datetime.now()
        metric_data = {
            'timestamp': timestamp,
            'value': value,
            'tags': tags or {}
        }
        cls._metrics[metric_name].append(metric_data)
        
        # 保持最近1000个数据点
        if len(cls._metrics[metric_name]) > 1000:
            cls._metrics[metric_name] = cls._metrics[metric_name][-1000:]
    
    @classmethod
    def get_metrics(cls, metric_name: str, time_range: timedelta = None) -> list:
        """获取性能指标"""
        metrics = cls._metrics.get(metric_name, [])
        
        if time_range:
            cutoff = datetime.now() - time_range
            metrics = [m for m in metrics if m['timestamp'] >= cutoff]
        
        return metrics
    
    @classmethod
    def get_summary(cls, metric_name: str, time_range: timedelta = None) -> Dict[str, Any]:
        """获取指标摘要"""
        metrics = cls.get_metrics(metric_name, time_range)
        
        if not metrics:
            return {}
        
        values = [m['value'] for m in metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'p95': sorted(values)[int(len(values) * 0.95)],
            'p99': sorted(values)[int(len(values) * 0.99)]
        }

def measure_performance(metric_name: str):
    """性能测量装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000  # 转换为毫秒
                PerformanceMonitor.record_metric(metric_name, execution_time)
                
                # 记录慢查询
                if execution_time > 1000:  # 超过1秒
                    logger.warning(
                        "慢操作检测: %s 耗时 %.2fms", 
                        metric_name, 
                        execution_time
                    )
        return wrapper
    return decorator

class SimpleCache:
    """简单内存缓存"""
    
    def __init__(self, default_ttl: int = 300):
        self._cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self._cache:
            return None
        
        data, expiry = self._cache[key]
        if datetime.now() > expiry:
            del self._cache[key]
            return None
        
        return data
    
    def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        now = datetime.now()
        valid_entries = {
            k: v for k, (data, expiry) in self._cache.items() 
            if expiry > now
        }
        
        return {
            'total_entries': len(self._cache),
            'valid_entries': len(valid_entries),
            'memory_usage': f"{len(str(self._cache))} bytes"
        }

# 全局缓存实例
cache = SimpleCache()

def cached(ttl: int = 300, key_func: Callable = None):
    """缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug("缓存命中: %s", cache_key)
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug("缓存设置: %s", cache_key)
            
            return result
        return wrapper
    return decorator