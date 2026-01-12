from models.product import Product
from models.transaction import Transaction
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    """库存服务"""
    
    @staticmethod
    def get_dashboard_stats():
        """获取仪表板统计"""
        try:
            # 基本统计
            products_data = Product.get_all()
            # 兼容不同的返回格式
            if isinstance(products_data, dict) and 'products' in products_data:
                products = products_data['products']
            else:
                products = products_data
                
            total_products = len(products) if products else 0
            
            # 安全计算库存总值
            total_inventory_value = 0
            if products:
                for product in products:
                    try:
                        quantity = float(product.get('quantity', 0) or 0)
                        price = float(product.get('price', 0) or 0)
                        total_inventory_value += quantity * price
                    except (ValueError, TypeError) as e:
                        logger.warning("计算产品库存价值时出错 (产品ID: %s): %s", product.get('id'), e)
                        continue
            
            # 今日交易统计
            today_incoming = 0
            today_outgoing = 0
            try:
                incoming, outgoing = Transaction.get_today_stats()
                today_incoming = incoming or 0
                today_outgoing = outgoing or 0
            except Exception as e:
                logger.warning("获取今日交易统计时出错: %s", e)
            
            # 低库存产品
            low_stock_count = 0
            try:
                if products:
                    low_stock_products = []
                    for p in products:
                        try:
                            min_stock = float(p.get('min_stock', 0) or 0)
                            quantity = float(p.get('quantity', 0) or 0)
                            if min_stock > 0 and quantity <= min_stock:
                                low_stock_products.append(p)
                        except (ValueError, TypeError) as e:
                            logger.warning("检查产品库存时出错 (产品ID: %s): %s", p.get('id'), e)
                            continue
                    low_stock_count = len(low_stock_products)
            except Exception as e:
                logger.warning("计算低库存产品数量时出错: %s", e)
            
            return {
                'total_products': total_products,
                'total_inventory_value': float(total_inventory_value),
                'today_incoming': today_incoming,
                'today_outgoing': today_outgoing,
                'low_stock_count': low_stock_count
            }
        except Exception as e:
            logger.exception("获取仪表板统计时发生未预期的错误: %s", e)
            # 返回默认值以避免前端崩溃
            return {
                'total_products': 0,
                'total_inventory_value': 0,
                'today_incoming': 0,
                'today_outgoing': 0,
                'low_stock_count': 0
            }
    
    @staticmethod
    def get_stock_alerts():
        """获取库存预警"""
        try:
            products_data = Product.get_all()
            # 兼容不同的返回格式
            if isinstance(products_data, dict) and 'products' in products_data:
                products = products_data['products']
            else:
                products = products_data
                
            alerts = []
            
            if not products:
                return alerts
                
            for product in products:
                try:
                    # 确保产品有必需的字段
                    quantity = float(product.get('quantity', 0) or 0)
                    min_stock = float(product.get('min_stock', 0) or 0)
                    name = product.get('name', '未知产品')
                    sku = product.get('sku', '')
                    
                    if quantity == 0:
                        status = 'zero'
                        message = '库存为零'
                    elif min_stock > 0 and quantity <= min_stock:
                        status = 'low'
                        message = '库存偏低'
                    else:
                        continue
                    
                    alerts.append({
                        'id': product.get('id', 0) or 0,
                        'product_name': name,
                        'sku': sku,
                        'current_quantity': quantity,
                        'min_stock': min_stock,
                        'status': status,
                        'message': message
                    })
                except (ValueError, TypeError) as e:
                    logger.warning("处理产品预警信息时出错 (产品ID: %s): %s", product.get('id'), e)
                    continue
                
            return alerts
        except Exception as e:
            logger.exception("获取库存预警时发生未预期的错误: %s", e)
            # 返回空列表以避免前端崩溃
            return []
    
    @staticmethod
    def calculate_bom_cost(bom_items):
        """计算BOM总成本"""
        if not bom_items:
            return 0
            
        total_cost = 0
        for item in bom_items:
            try:
                total_cost += float(item.get('item_cost', 0) or 0)
            except (ValueError, TypeError) as e:
                logger.warning("计算BOM项成本时出错: %s", e)
                continue
                
        return total_cost
    
    @staticmethod
    def calculate_material_cost_with_shipping(bom_items, total_quantity, shipping_cost=0):
        """计算包含快递费用的物料成本
        
        Args:
            bom_items: BOM项目列表
            total_quantity: 总生产数量
            shipping_cost: 快递费用
            
        Returns:
            包含分摊快递费用的BOM项目列表
        """
        if not bom_items:
            return []
        
        # 计算所有物料的总成本
        total_material_cost = 0
        for item in bom_items:
            try:
                total_material_cost += float(item.get('item_cost', 0) or 0)
            except (ValueError, TypeError) as e:
                logger.warning("计算物料成本时出错: %s", e)
                continue
        
        # 如果没有物料成本，直接返回原列表
        if total_material_cost <= 0:
            return bom_items
            
        # 计算快递费用分摊系数
        shipping_cost_per_unit = shipping_cost / total_material_cost if total_material_cost > 0 else 0
        
        # 为每个BOM项添加分摊的快递费用
        updated_bom_items = []
        for item in bom_items:
            try:
                # 复制原始项
                updated_item = item.copy()
                
                # 计算该项分摊的快递费用
                item_material_cost = float(item.get('item_cost', 0) or 0)
                allocated_shipping_cost = item_material_cost * shipping_cost_per_unit
                
                # 更新成本信息
                updated_item['shipping_cost'] = allocated_shipping_cost
                updated_item['total_cost_with_shipping'] = item_material_cost + allocated_shipping_cost
                
                updated_bom_items.append(updated_item)
            except (ValueError, TypeError) as e:
                logger.warning("处理BOM项快递费用时出错: %s", e)
                # 即使出错也添加原始项
                updated_bom_items.append(item)
                continue
            
        return updated_bom_items