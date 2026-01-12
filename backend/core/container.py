"""依赖注入容器"""
from typing import Type, TypeVar, Dict, Any, Callable
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DependencyContainer:
    """依赖注入容器"""
    
    _instance = None
    _services = {}
    _singletons = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, interface: Type, implementation: Type = None, singleton: bool = False):
        """注册服务"""
        def decorator(impl):
            self._services[interface] = {
                'implementation': impl,
                'singleton': singleton,
                'instance': None
            }
            return impl
        
        if implementation is None:
            return decorator
        else:
            self._services[interface] = {
                'implementation': implementation,
                'singleton': singleton,
                'instance': None
            }
    
    def get(self, interface: Type[T]) -> T:
        """获取服务实例"""
        if interface not in self._services:
            raise ValueError(f"服务未注册: {interface}")
        
        service_config = self._services[interface]
        
        if service_config['singleton']:
            if service_config['instance'] is None:
                service_config['instance'] = service_config['implementation']()
            return service_config['instance']
        else:
            return service_config['implementation']()
    
    def register_instance(self, interface: Type, instance: Any):
        """注册单例实例"""
        self._services[interface] = {
            'implementation': type(instance),
            'singleton': True,
            'instance': instance
        }

# 全局容器实例
container = DependencyContainer()

def injectable(singleton: bool = False):
    """可注入装饰器"""
    def decorator(cls):
        container.register(cls, cls, singleton=singleton)
        return cls
    return decorator

def inject(interface: Type):
    """注入装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取依赖实例
            dependency = container.get(interface)
            # 查找参数位置
            import inspect
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            
            # 注入依赖
            if params and params[0] == 'self':
                # 实例方法
                kwargs[params[1]] = dependency
            else:
                # 函数或静态方法
                kwargs[params[0]] = dependency
            
            return func(*args, **kwargs)
        return wrapper
    return decorator