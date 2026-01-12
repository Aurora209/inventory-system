"""应用工厂优化"""
from flask import Flask
import logging
from typing import Optional

# 修复：避免循环导入，简化导入路径
from utils.database import init_database
from utils.performance import PerformanceMonitor
from utils.documentation import APIDoc
from utils.api_response import APIResponse

logger = logging.getLogger(__name__)

class ApplicationFactory:
    """应用工厂"""
    
    @staticmethod
    def create_app(config_name: Optional[str] = None) -> Flask:
        """创建优化后的Flask应用"""
        
        # 1. 创建Flask应用
        from config import config_dict_legacy
        app = Flask(__name__)
        
        # 2. 加载配置
        if config_name in ['development', 'production', 'testing']:
            app.config.from_object(config_dict_legacy[config_name])
        else:
            app.config.from_object(config_dict_legacy['development'])
        
        # 3. 初始化各个组件
        ApplicationFactory._setup_logging(app)
        ApplicationFactory._setup_database(app)
        ApplicationFactory._setup_dependencies(app)
        ApplicationFactory._setup_extensions(app)
        ApplicationFactory._setup_blueprints(app)
        ApplicationFactory._setup_event_handlers(app)
        ApplicationFactory._setup_task_queue(app)
        ApplicationFactory._setup_monitoring(app)
        ApplicationFactory._setup_documentation(app)
        
        logger.info("Flask应用创建完成")
        return app
    
    @staticmethod
    def _setup_logging(app: Flask):
        """设置日志"""
        try:
            from logging_config import setup_logging
            setup_logging(debug=app.config['DEBUG'])
        except Exception as e:
            logging.basicConfig(level=logging.INFO)
            logger.warning("日志配置加载失败: %s", e)
    
    @staticmethod
    def _setup_database(app: Flask):
        """初始化数据库"""
        try:
            init_database()
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error("数据库初始化失败: %s", e)
            raise
    
    @staticmethod
    def _setup_dependencies(app: Flask):
        """设置依赖注入"""
        # 注册配置
        # 简化依赖注入实现
        try:
            from core.container import container
            from config import config_dict_legacy
            
            container.register_instance(dict, app.config)
            
            # 注册服务
            from services.order_service import OrderService
            from services.inventory_service import InventoryService
            from services.category_service import CategoryService
            
            container.register(OrderService, singleton=True)
            container.register(InventoryService, singleton=True)
            container.register(CategoryService, singleton=True)
            
            logger.debug("依赖注入设置完成")
        except Exception as e:
            logger.warning("依赖注入设置失败: %s", e)
    
    @staticmethod
    def _setup_extensions(app: Flask):
        """初始化扩展"""
        from flask_cors import CORS
        
        CORS(app, resources={r"/api/*": {"origins": "*"}})
        logger.debug("扩展初始化完成")
    
    @staticmethod
    def _setup_blueprints(app: Flask):
        """注册蓝图"""
        from routes.categories import categories_bp
        from routes.products import products_bp
        from routes.bom import bom_bp
        from routes.dashboard import dashboard_bp
        from routes.orders import orders_bp
        from routes.production import production_bp
        from routes.transactions import transactions_bp
        from routes.inventory import inventory_bp
        
        blueprints = [
            (categories_bp, '/api'),
            (products_bp, '/api'),
            (bom_bp, '/api'),
            (dashboard_bp, '/api'),
            (orders_bp, '/api'),
            (production_bp, '/api'),
            (transactions_bp, '/api'),
            (inventory_bp, '/api')
        ]
        
        for blueprint, url_prefix in blueprints:
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        
        logger.info("蓝图注册完成: 总数=%s", len(blueprints))
    
    @staticmethod
    def _setup_event_handlers(app: Flask):
        """设置事件处理器"""
        # 简化事件处理，避免复杂依赖
        try:
            # 导入事件处理器以确保它们被注册
            from core.events import event_bus, ProductEventHandlers, OrderEventHandlers
            
            # 启动事件总线
            event_bus.start()
            logger.debug("事件系统启动完成")
        except Exception as e:
            logger.warning("事件系统启动失败: %s", e)
    
    @staticmethod
    def _setup_task_queue(app: Flask):
        """设置任务队列"""
        try:
            # 启动任务队列
            from core.tasks import task_queue
            task_queue.start(worker_count=2)
            logger.debug("任务队列启动完成")
        except Exception as e:
            logger.warning("任务队列启动失败: %s", e)
    
    @staticmethod
    def _setup_monitoring(app: Flask):
        """设置性能监控"""
        # 添加性能监控端点
        @app.route('/api/monitoring/metrics')
        def get_metrics():
            try:
                from utils.performance import PerformanceMonitor
                
                metrics = {
                    'database_queries': PerformanceMonitor.get_summary('database_query'),
                    'api_requests': PerformanceMonitor.get_summary('api_request'),
                    'cache_stats': PerformanceMonitor.get_summary('cache_hit')
                }
                
                return APIResponse.success(data=metrics, message="监控指标获取成功")
            except Exception as e:
                logger.error("监控指标获取失败: %s", e)
                return APIResponse.error("监控指标获取失败")
        
        logger.debug("性能监控设置完成")
    
    @staticmethod
    def _setup_documentation(app: Flask):
        """设置API文档"""
        @app.route('/api/docs')
        def api_docs():
            try:
                from utils.documentation import APIDoc
                
                docs = APIDoc.get_documentation()
                openapi_spec = APIDoc.generate_openapi_spec()
                
                return APIResponse.success(
                    data={
                        'endpoints': docs,
                        'openapi_spec': openapi_spec
                    },
                    message="API文档获取成功"
                )
            except Exception as e:
                logger.error("API文档获取失败: %s", e)
                return APIResponse.error("API文档获取失败")
        
        logger.debug("API文档设置完成")

def create_app(config_name: Optional[str] = None) -> Flask:
    """创建应用的工厂函数"""
    return ApplicationFactory.create_app(config_name)