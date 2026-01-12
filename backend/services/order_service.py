"""优化后的订单服务"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import string
import logging
from decimal import Decimal

from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from models.transaction import Transaction
from utils.database import db_manager
from utils.error_handler import ValidationError, DatabaseError
from utils.validators import DataValidator, OrderValidator

logger = logging.getLogger(__name__)

class OrderNumberGenerator:
    """订单号生成器"""
    
    @staticmethod
    def generate(prefix: str = 'ORD') -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_str}"

class OrderCalculator:
    """订单计算器"""
    
    @staticmethod
    def calculate_order_total(items: List[Dict[str, Any]], shipping_cost: float = 0) -> Dict[str, Any]:
        """计算订单总金额"""
        if not items:
            return {
                'items_total': 0.0,
                'shipping_cost': shipping_cost,
                'order_total': shipping_cost
            }
        
        items_total = sum(
            float(item.get('quantity', 0)) * float(item.get('unit_price', 0))
            for item in items
        )
        
        return {
            'items_total': items_total,
            'shipping_cost': shipping_cost,
            'order_total': items_total + shipping_cost
        }
    
    @staticmethod
    def allocate_shipping_cost(items: List[Dict[str, Any]], shipping_cost: float) -> List[Dict[str, Any]]:
        """分摊运费到订单项"""
        if not items or shipping_cost <= 0:
            return items
        
        # 计算订单项总金额
        items_total = sum(float(item.get('total_price', 0)) for item in items)
        if items_total <= 0:
            return items
        
        # 计算分摊比例
        shipping_ratio = shipping_cost / items_total
        
        # 分摊运费
        updated_items = []
        for item in items:
            updated_item = item.copy()
            item_total = float(item.get('total_price', 0))
            allocated_shipping = item_total * shipping_ratio
            
            # 计算新的单价（包含分摊的运费）
            quantity = float(item.get('quantity', 1))
            original_unit_price = float(item.get('unit_price', 0))
            adjusted_unit_price = (item_total + allocated_shipping) / quantity if quantity > 0 else original_unit_price
            
            updated_item['allocated_shipping'] = allocated_shipping
            updated_item['adjusted_unit_price'] = adjusted_unit_price
            updated_items.append(updated_item)
        
        return updated_items

class OrderTransactionCreator:
    """订单交易记录创建器"""
    
    @staticmethod
    def create_from_order(order: Dict[str, Any]) -> bool:
        """从订单创建库存交易记录"""
        try:
            order_type = order.get('order_type')
            order_items = order.get('items', [])
            
            if order_type == 'purchase':
                return OrderTransactionCreator._create_purchase_transactions(order, order_items)
            elif order_type == 'sales':
                return OrderTransactionCreator._create_sales_transactions(order, order_items)
            else:
                logger.warning("未知的订单类型: %s", order_type)
                return False
                
        except Exception as e:
            logger.error("创建订单交易记录失败: %s", e)
            raise DatabaseError(f"创建交易记录失败: {str(e)}")
    
    @staticmethod
    def _create_purchase_transactions(order: Dict[str, Any], items: List[Dict[str, Any]]) -> bool:
        """创建采购订单交易记录"""
        shipping_cost = float(order.get('shipping_cost', 0))
        
        # 如果有运费，需要分摊
        if shipping_cost > 0:
            items_with_shipping = OrderCalculator.allocate_shipping_cost(items, shipping_cost)
        else:
            items_with_shipping = items
        
        for item in items_with_shipping:
            if not item.get('product_id'):
                continue
            
            product_id = int(item['product_id'])
            quantity = float(item.get('quantity', 0))
            
            # 使用调整后的单价（如果存在）
            unit_price = item.get('adjusted_unit_price', item.get('unit_price', 0))
            
            Transaction.create(
                product_id,
                'in',
                quantity,
                unit_price,
                datetime.now().date().isoformat(),
                reference_no=str(order.get('order_number', '')),
                customer_supplier=str(order.get('customer_supplier', '')),
                notes=f"采购订单 #{order.get('order_number', '')}"
            )
        
        return True
    
    @staticmethod
    def _create_sales_transactions(order: Dict[str, Any], items: List[Dict[str, Any]]) -> bool:
        """创建销售订单交易记录"""
        for item in items:
            if not item.get('product_id'):
                continue
            
            product_id = int(item['product_id'])
            quantity = float(item.get('quantity', 0))
            unit_price = float(item.get('unit_price', 0))
            
            Transaction.create(
                product_id,
                'out',
                quantity,
                unit_price,
                datetime.now().date().isoformat(),
                reference_no=str(order.get('order_number', '')),
                customer_supplier=str(order.get('customer_supplier', '')),
                notes=f"销售订单 #{order.get('order_number', '')}"
            )
        
        return True

class OrderService:
    """优化后的订单服务"""
    
    @staticmethod
    def create_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建订单"""
        logger.info("创建订单: %s", order_data.get('order_number', '新订单'))
        
        # 数据验证
        validated_data = OrderService._validate_order_data(order_data)
        
        # 计算订单金额
        calculation = OrderCalculator.calculate_order_total(
            validated_data.get('items', []),
            validated_data.get('shipping_cost', 0)
        )
        
        # 生成订单号（如果没有提供）
        if not validated_data.get('order_number'):
            validated_data['order_number'] = OrderNumberGenerator.generate()
        
        # 设置计算后的金额
        validated_data['total_amount'] = calculation['order_total']
        
        # 创建订单
        with db_manager.get_connection() as conn:
            try:
                # 创建订单主记录
                order = Order.create(**validated_data)
                conn.commit()
                
                logger.info("订单创建成功: ID=%s, 订单号=%s", order['id'], order['order_number'])
                return order
                
            except Exception as e:
                conn.rollback()
                logger.error("订单创建失败: %s", e)
                raise DatabaseError(f"订单创建失败: {str(e)}")
    
    @staticmethod
    def update_order(order_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新订单"""
        logger.info("更新订单: ID=%s", order_id)
        
        DataValidator.validate_integer(order_id, 'order_id', min_value=1)
        
        # 检查订单是否存在
        existing_order = Order.get_by_id(order_id)
        if not existing_order:
            raise ValidationError("订单不存在")
        
        # 记录原始状态（用于状态变更检查）
        original_status = existing_order['status']
        
        # 验证更新数据
        validated_data = OrderService._validate_update_data(update_data)
        
        # 如果更新了订单项，重新计算金额
        if 'items' in validated_data:
            calculation = OrderCalculator.calculate_order_total(
                validated_data['items'],
                validated_data.get('shipping_cost', existing_order.get('shipping_cost', 0))
            )
            validated_data['total_amount'] = calculation['order_total']
        
        # 更新订单
        with db_manager.get_connection() as conn:
            try:
                updated_order = Order.update(order_id, **validated_data)
                conn.commit()
                
                # 检查是否需要创建交易记录
                new_status = validated_data.get('status')
                if (original_status != 'completed' and 
                    new_status == 'completed' and 
                    updated_order):
                    OrderTransactionCreator.create_from_order(updated_order)
                
                logger.info("订单更新成功: ID=%s", order_id)
                return updated_order
                
            except Exception as e:
                conn.rollback()
                logger.error("订单更新失败: %s", e)
                raise DatabaseError(f"订单更新失败: {str(e)}")
    
    @staticmethod
    def _validate_order_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证订单数据"""
        from utils.validators import OrderValidator
        return OrderValidator.validate_create_data(data)
    
    @staticmethod
    def _validate_update_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证订单更新数据"""
        validated_data = {}
        
        if 'order_type' in data:
            order_type = DataValidator.validate_string(data['order_type'], 'order_type')
            if order_type not in ['purchase', 'sales']:
                raise ValidationError("订单类型必须是 'purchase' 或 'sales'")
            validated_data['order_type'] = order_type
        
        if 'customer_supplier' in data:
            validated_data['customer_supplier'] = DataValidator.validate_string(
                data['customer_supplier'], 'customer_supplier', min_length=1, max_length=100
            )
        
        if 'order_date' in data:
            validated_data['order_date'] = DataValidator.validate_string(data['order_date'], 'order_date')
        
        if 'status' in data:
            status = DataValidator.validate_string(data['status'], 'status')
            if status not in ['pending', 'completed', 'cancelled']:
                raise ValidationError("订单状态无效")
            validated_data['status'] = status
        
        if 'shipping_cost' in data:
            # 保证 shipping_cost 为 float，避免与 float 类型相加时出现 Decimal 类型错误
            validated_data['shipping_cost'] = float(DataValidator.validate_decimal(
                data['shipping_cost'], 'shipping_cost', min_value=Decimal('0')
            ))
        
        if 'notes' in data:
            validated_data['notes'] = DataValidator.validate_string(
                data['notes'], 'notes', min_length=0, max_length=500
            )
        
        # 验证订单项
        if 'items' in data and isinstance(data['items'], list):
            validated_data['items'] = DataValidator.validate_order_items(data['items'])
        
        # 卖方信息
        seller_fields = ['seller_name', 'seller_address', 'seller_phone', 'seller_taxNo', 'seller_note']
        for field in seller_fields:
            if field in data:
                validated_data[field] = DataValidator.validate_string(
                    data[field], field, min_length=0, max_length=200
                ) if data[field] else None
        
        return validated_data
    
    @staticmethod
    def get_order_statistics() -> Dict[str, Any]:
        """获取订单统计信息"""
        all_orders = Order.get_all()
        
        stats = {
            'total_orders': len(all_orders),
            'by_type': {
                'purchase': 0,
                'sales': 0
            },
            'by_status': {
                'pending': 0,
                'completed': 0,
                'cancelled': 0
            },
            'amounts': {
                'total': 0.0,
                'purchase': 0.0,
                'sales': 0.0
            }
        }
        
        for order in all_orders:
            order_type = order['order_type']
            status = order['status']
            amount = float(order.get('total_amount', 0))
            
            # 统计类型
            stats['by_type'][order_type] = stats['by_type'].get(order_type, 0) + 1
            
            # 统计状态
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # 统计金额
            stats['amounts']['total'] += amount
            stats['amounts'][order_type] += amount
        
        return stats
    
    @staticmethod
    def export_orders_to_dict(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将订单数据导出为字典格式（用于报表等）"""
        exported_orders = []
        
        for order in orders:
            exported_order = {
                'id': order['id'],
                'order_number': order.get('order_number', ''),
                'order_type': order['order_type'],
                'customer_supplier': order['customer_supplier'],
                'order_date': order['order_date'],
                'total_amount': float(order.get('total_amount', 0)),
                'shipping_cost': float(order.get('shipping_cost', 0)),
                'status': order.get('status', 'pending'),
                'created_at': order.get('created_at', ''),
                'items': []
            }
            
            # 添加订单项
            for item in order.get('items', []):
                exported_item = {
                    'product_id': item.get('product_id'),
                    'product_name': item.get('product_name', ''),
                    'description': item.get('description', ''),
                    'quantity': float(item.get('quantity', 0)),
                    'unit_price': float(item.get('unit_price', 0)),
                    'total_price': float(item.get('total_price', 0)),
                    'unit': item.get('unit', '个')
                }
                exported_order['items'].append(exported_item)
            
            exported_orders.append(exported_order)
        
        return exported_orders