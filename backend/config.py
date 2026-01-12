"""修复后的配置文件 - 不依赖pydantic"""
import os
import logging
from typing import ClassVar, Optional, Dict, Any

logger = logging.getLogger(__name__)

class BaseConfig:
    """基础配置类"""
    
    # 基础路径配置
    BASE_DIR: ClassVar[str] = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR: ClassVar[str] = os.path.join(BASE_DIR, 'data')
    LOG_DIR: ClassVar[str] = os.path.join(BASE_DIR, 'logs')
    
    # 数据库配置
    DATABASE_PATH: ClassVar[str] = os.path.join(DATA_DIR, 'inventory.db')
    SQLALCHEMY_DATABASE_URI: ClassVar[str] = f'sqlite:///{DATABASE_PATH}'
    
    # 应用配置
    DEBUG: bool = False
    TESTING: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # API配置
    API_PREFIX: str = "/api"
    CORS_ORIGINS: str = "*"
    
    # 备份配置
    BACKUP_ENABLED: bool = True
    BACKUP_KEEP_COUNT: int = 10
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def ensure_data_dir(cls):
        """确保数据目录存在"""
        if not os.path.exists(cls.DATA_DIR):
            os.makedirs(cls.DATA_DIR)
            logger.info("创建数据目录: %s", cls.DATA_DIR)
        
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)
            logger.info("创建日志目录: %s", cls.LOG_DIR)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            key: value for key, value in self.__class__.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }

class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProductionConfig(BaseConfig):
    """生产环境配置"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000,https://yourdomain.com"

class TestingConfig(BaseConfig):
    """测试环境配置"""
    TESTING: bool = True
    DEBUG: bool = True
    DATABASE_PATH: ClassVar[str] = os.path.join(BaseConfig.DATA_DIR, 'test_inventory.db')

# 配置字典
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

def get_config(config_name: Optional[str] = None) -> BaseConfig:
    """获取配置实例"""
    if not config_name:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    
    config_class = config_dict.get(config_name, DevelopmentConfig)
    return config_class()

# 默认配置实例
config = get_config()

# 向后兼容的配置字典
config_dict_legacy = {
    'development': DevelopmentConfig(),
    'production': ProductionConfig(),
    'testing': TestingConfig(),
}