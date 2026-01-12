"""增强的配置管理"""
import os
import logging
from typing import Dict, Any, Optional
from pydantic import BaseSettings, validator, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    driver: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    name: str = "inventory.db"
    user: str = ""
    password: str = ""
    pool_size: int = 5
    pool_recycle: int = 3600
    
    @property
    def url(self) -> str:
        """构建数据库URL"""
        if self.driver == "sqlite":
            return f"sqlite:///data/{self.name}"
        elif self.driver == "postgresql":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        else:
            raise ValueError(f"不支持的数据库驱动: {self.driver}")

class LoggingConfig(BaseSettings):
    """日志配置"""
    level: str = "INFO"
    format: str = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    file: Optional[str] = "backend.log"
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

class SecurityConfig(BaseSettings):
    """安全配置"""
    secret_key: str = Field(..., min_length=32)
    cors_origins: str = "*"
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY必须至少32个字符")
        return v

class CacheConfig(BaseSettings):
    """缓存配置"""
    enabled: bool = True
    default_ttl: int = 300  # 5分钟
    backend: str = "memory"  # memory, redis
    redis_url: str = "redis://localhost:6379/0"

class AppConfig(BaseSettings):
    """应用配置"""
    
    # 基础配置
    debug: bool = False
    testing: bool = False
    environment: str = "development"
    
    # 各个模块配置
    database: DatabaseConfig = DatabaseConfig()
    logging: LoggingConfig = LoggingConfig()
    security: SecurityConfig = SecurityConfig()
    cache: CacheConfig = CacheConfig()
    
    # API配置
    api_prefix: str = "/api"
    docs_enabled: bool = True
    
    class Config:
        env_prefix = "APP_"
        case_sensitive = False
        env_nested_delimiter = "__"

class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _config: AppConfig = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def load_config(cls, environment: str = None) -> AppConfig:
        """加载配置"""
        if cls._config is None:
            env = environment or os.getenv("FLASK_ENV", "development")
            cls._config = AppConfig(_env_file=f".env.{env}")
            logger.info("配置加载完成: 环境=%s", env)
        
        return cls._config
    
    @classmethod
    def get_config(cls) -> AppConfig:
        """获取配置"""
        if cls._config is None:
            return cls.load_config()
        return cls._config
    
    @classmethod
    def reload_config(cls) -> AppConfig:
        """重新加载配置"""
        cls._config = None
        return cls.load_config()

# 全局配置实例
config = ConfigManager.get_config()