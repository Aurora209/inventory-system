"""修复后的Flask应用主文件"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging

# 使用修复后的配置
from config import config, config_dict_legacy

def create_app(config_name=None):
    app = Flask(__name__)

    # 初始化日志配置
    try:
        from logging_config import setup_logging
        setup_logging(False)
    except Exception:
        pass

    # 根据环境变量或参数选择配置
    if not config_name:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    
    # 修复：使用正确的配置方式
    if config_name in ['development', 'production', 'testing']:
        app.config.from_object(config_dict_legacy[config_name])
    else:
        app.config.from_object(config_dict_legacy['development'])

    # 使用配置中的 DEBUG 值设置日志
    try:
        from logging_config import setup_logging
        setup_logging(app.config.get('DEBUG', False))
    except Exception as e:
        logging.getLogger(__name__).warning(f"无法加载日志配置: {e}")

    # 确保数据目录存在
    config_dict_legacy['development'].ensure_data_dir()

    # 初始化扩展
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 注册路由
    from routes.categories import categories_bp
    from routes.products import products_bp
    from routes.bom import bom_bp
    from routes.dashboard import dashboard_bp
    from routes.orders import orders_bp
    from routes.production import production_bp
    from routes.transactions import transactions_bp
    from routes.inventory import inventory_bp
    
    app.register_blueprint(categories_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(bom_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(production_bp, url_prefix='/api')
    app.register_blueprint(transactions_bp, url_prefix='/api')
    app.register_blueprint(inventory_bp, url_prefix='/api')

    # 初始化数据库
    try:
        from utils.database import init_database
        init_database()
        logging.getLogger(__name__).info("数据库初始化完成")
    except Exception as e:
        logging.getLogger(__name__).error(f"数据库初始化失败: {e}")
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '资源未找到'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': '服务器内部错误'}), 500
    
    # 健康检查
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy', 
            'message': '库存管理系统API运行正常',
            'database_path': config.DATABASE_PATH
        })
    
    # API根路径
    @app.route('/')
    def index():
        return jsonify({
            'message': '库存管理系统API',
            'version': '1.0.0',
            'database_location': config.DATABASE_PATH,
            'endpoints': {
                'categories': '/api/categories',
                'products': '/api/products',
                'bom': '/api/bom',
                'dashboard': '/api/dashboard',
                'transactions': '/api/transactions',
                'orders': '/api/orders',
                'production': '/api/production',
                'inventory': '/api/inventory'
            }
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=app.config['DEBUG'],
        use_reloader=False
    )