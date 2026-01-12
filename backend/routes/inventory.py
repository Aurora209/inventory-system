from flask import Blueprint, request, jsonify
import logging
from models.product import Product
from models.transaction import Transaction
from datetime import datetime

logger = logging.getLogger(__name__)

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory/check', methods=['POST'])
def inventory_check():
    """库存盘点"""
    try:
        logger.debug('inventory_check called')
        data = request.get_json()
        items = data.get('items', [])

        if not items:
            logger.warning('盘点项目为空')
            return jsonify({
                'success': False,
                'data': None,
                'message': '盘点项目不能为空',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 记录盘点结果
        check_results = []
        for item in items:
            product_id = item.get('product_id')
            system_quantity = item.get('system_quantity')
            actual_quantity = item.get('actual_quantity')
            difference = item.get('difference')
            
            if product_id is None or actual_quantity is None:
                continue
            
            # 更新产品库存
            product = Product.get_by_id(product_id)
            if product:
                # 计算需要调整的数量
                adjust_quantity = actual_quantity - system_quantity
                
                # 如果有差异，创建调整交易记录
                if adjust_quantity != 0:
                    transaction_type = 'in' if adjust_quantity > 0 else 'out'
                    abs_quantity = abs(adjust_quantity)
                    
                    # 创建库存调整交易记录
                    transaction = Transaction.create(
                        product_id=product_id,
                        transaction_type=transaction_type,
                        quantity=abs_quantity,
                        unit_price=product['price'] if product['price'] else 0,
                        transaction_date=datetime.now().strftime('%Y-%m-%d'),
                        reference_no=f'CHECK-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        notes=f'库存盘点调整: 系统数量 {system_quantity}, 实际数量 {actual_quantity}'
                    )
                    
                    # 更新产品库存
                    Product.update_stock(product_id, actual_quantity)
                
                check_results.append({
                    'product_id': product_id,
                    'system_quantity': system_quantity,
                    'actual_quantity': actual_quantity,
                    'difference': difference
                })
        
        return jsonify({
            'success': True,
            'data': {
                'results': check_results
            },
            'message': '库存盘点完成',
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.exception('Error in inventory_check: %s', e)
        return jsonify({
            'success': False,
            'data': None,
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500