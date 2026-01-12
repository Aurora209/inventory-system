from flask import Blueprint, jsonify
import logging

from services.inventory_service import InventoryService
from models.transaction import Transaction
from models.product import Product

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """获取仪表板数据"""
    try:
        logger.debug('get_dashboard called')
        stats = InventoryService.get_dashboard_stats()

        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'total_products': stats.get('total_products', 0),
                    'total_inventory_value': float(stats.get('total_inventory_value', 0)),
                    'today_incoming': stats.get('today_incoming', 0),
                    'today_outgoing': stats.get('today_outgoing', 0),
                    'low_stock_count': stats.get('low_stock_count', 0)
                }
            },
            'message': '获取仪表板数据成功',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception('Error in get_dashboard: %s', e)
        return jsonify({
            'success': False,
            'data': None,
            'message': f'获取仪表板数据失败: {str(e)}',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }), 500

@dashboard_bp.route('/dashboard/alerts', methods=['GET'])
def get_stock_alerts():
    """获取库存预警"""
    try:
        logger.debug('get_stock_alerts called')
        alerts = InventoryService.get_stock_alerts()

        # 调整数据格式以匹配前端期望
        formatted_alerts = []
        for alert in alerts:
            name = alert.get('product_name', '未知产品')
            sku = alert.get('sku', '')
            quantity = alert.get('current_quantity', 0) or 0
            min_stock = alert.get('min_stock', 0) or 0

            formatted_alert = {
                'id': alert.get('id', 0) or 0,
                'product_name': name,
                'sku': sku,
                'current_quantity': quantity,
                'min_stock': min_stock,
                'status': 'low' if quantity <= min_stock and quantity > 0 else 'zero'
            }
            formatted_alerts.append(formatted_alert)

        return jsonify({
            'success': True,
            'data': {
                'alerts': formatted_alerts
            },
            'message': '获取库存预警成功',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception('Error in get_stock_alerts: %s', e)
        return jsonify({
            'success': False,
            'data': None,
            'message': f'获取库存预警失败: {str(e)}',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }), 500

@dashboard_bp.route('/dashboard/transactions', methods=['GET'])
def get_recent_transactions():
    """获取最近交易记录"""
    try:
        logger.debug('get_recent_transactions called')
        transactions = Transaction.get_recent(5)  # 获取最近5条记录

        # 调整数据格式以匹配前端期望
        formatted_transactions = []
        for transaction in transactions:
            # 获取产品信息
            product = None
            try:
                if transaction.get('product_id'):
                    product = Product.get_by_id(transaction['product_id'])
            except Exception as e:
                logger.warning("获取产品信息失败 (产品ID: %s): %s", transaction.get('product_id'), e)
            
            formatted_transaction = {
                'id': transaction.get('id', 0),
                'product_name': product.get('name', '未知产品') if product else transaction.get('product_name', '未知产品'),
                'transaction_type': transaction.get('transaction_type', ''),
                'quantity': transaction.get('quantity', 0),
                'transaction_date': transaction.get('transaction_date', '')
            }
            formatted_transactions.append(formatted_transaction)

        return jsonify({
            'success': True,
            'data': {
                'transactions': formatted_transactions
            },
            'message': '获取最近交易记录成功',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        logger.exception('Error in get_recent_transactions: %s', e)
        return jsonify({
            'success': False,
            'data': None,
            'message': f'获取最近交易记录失败: {str(e)}',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }), 500