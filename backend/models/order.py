import logging
from models.base import BaseModel
from models.order_item import OrderItem
from models.product import Product
from utils.database import serialize_rows
from datetime import datetime

logger = logging.getLogger(__name__)

class Order(BaseModel):
    """订单模型"""
    
    @classmethod
    def create_table(cls):
        """创建订单表"""
        query = '''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                order_type TEXT NOT NULL,
                customer_supplier TEXT NOT NULL,
                order_date DATE NOT NULL,
                total_amount DECIMAL(10,2) DEFAULT 0,
                shipping_cost DECIMAL(10,2) DEFAULT 0,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                seller_name TEXT,
                seller_address TEXT,
                seller_phone TEXT,
                seller_taxNo TEXT,
                seller_note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        cls.execute_query(query)
        # 确保旧数据库在表存在的情况下也能添加新的列（向后兼容）
        try:
            cols = [r[1] for r in cls.execute_query("PRAGMA table_info(orders)")]
            # 列出需要确保存在的列及其 SQL 类型
            extras = {
                'seller_name': 'TEXT',
                'seller_address': 'TEXT',
                'seller_phone': 'TEXT',
                'seller_taxNo': 'TEXT',
                'seller_note': 'TEXT',
                'shipping_cost': 'DECIMAL(10,2)',
                'status': 'TEXT'
            }
            for col, typ in extras.items():
                if col not in cols:
                    alter_sql = f'ALTER TABLE orders ADD COLUMN {col} {typ}'
                    if col == 'shipping_cost':
                        alter_sql += ' DEFAULT 0'
                    elif col == 'status':
                        alter_sql += " DEFAULT 'pending'"
                    try:
                        cls.execute_query(alter_sql)
                    except Exception:
                        # 如果失败（例如并发或权限问题），忽略以保持兼容性
                        pass
        except Exception:
            # 如果无法查询表结构（例如表不存在），忽略，这种情况会在下一次创建时被覆盖
            pass
    
    @classmethod
    def get_all(cls, order_type=None, status=None):
        """获取所有订单"""
        query = 'SELECT * FROM orders WHERE 1=1'
        params = []
        
        if order_type:
            query += ' AND order_type = ?'
            params.append(order_type)
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY order_date DESC, created_at DESC'
        
        rows = cls.execute_query(query, params)
        orders = serialize_rows(rows)
        
        # 为每个订单获取订单项
        for order in orders:
            order['items'] = OrderItem.get_by_order_id(order['id'])
            
            # 处理箱子信息，确保前端能正确显示
            for item in order['items']:
                # 小箱信息
                if item.get('small_box_length') is not None:
                    item['smallBox'] = {
                        'length': item['small_box_length'],
                        'width': item['small_box_width'],
                        'height': item['small_box_height'],
                        'weight': item['small_box_weight']
                    }
                
                # 大箱信息
                if item.get('large_box_length') is not None:
                    item['largeBox'] = {
                        'units_per_box': item['large_box_units_per_box'],
                        'length': item['large_box_length'],
                        'width': item['large_box_width'],
                        'height': item['large_box_height'],
                        'weight': item['large_box_weight']
                    }
        
        return orders
    
    @classmethod
    def create(cls, order_type, customer_supplier, order_date, total_amount=0, shipping_cost=0, notes=None, items=None, order_number=None, seller_name=None, seller_address=None, seller_phone=None, seller_taxNo=None, seller_note=None, status='pending'):
        """创建订单

        支持传入 order_number（若提供则不会自动生成），并可存储卖方信息字段。
        """
        # 如果没有提供 order_number，则自动生成一个
        if not order_number:
            order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"

        query = '''
            INSERT INTO orders (order_number, order_type, customer_supplier, order_date, total_amount, shipping_cost, notes, seller_name, seller_address, seller_phone, seller_taxNo, seller_note, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        # 使用数据库连接上下文管理器确保事务正确处理
        from utils.database import get_db_connection
        with get_db_connection() as conn:
            try:
                # 插入订单，将Decimal类型转换为float以避免sqlite3绑定错误
                cursor = conn.execute(query, (
                    order_number, 
                    order_type, 
                    customer_supplier, 
                    order_date, 
                    float(total_amount) if total_amount is not None else 0, 
                    float(shipping_cost) if shipping_cost is not None else 0, 
                    notes, 
                    seller_name, 
                    seller_address, 
                    seller_phone, 
                    seller_taxNo, 
                    seller_note, 
                    status
                ))
                conn.commit()
                order_id = cursor.lastrowid
                
                # 如果有订单项，则创建订单项
                if items:
                    for item in items:
                        # 计算总价
                        quantity = float(item.get('quantity', 1))
                        unit_price = float(item.get('unit_price', 0))
                        total_price = quantity * unit_price

                        # 如果传入的 unit 为空字符串或 None，则尝试使用产品表中的单位作为回退
                        unit_val = item.get('unit')
                        if not unit_val:
                            try:
                                prod = Product.get_by_id(item.get('product_id')) if item.get('product_id') else None
                                unit_val = prod.get('unit') if prod and prod.get('unit') else '个'
                            except Exception:
                                unit_val = '个'

                        item_query = '''
                            INSERT INTO order_items 
                            (order_id, product_id, description, quantity, unit_price, total_price, unit, units_per_box, packaging, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        '''
                        conn.execute(item_query, (
                            order_id,
                            item.get('product_id'),
                            item.get('description', ''),  # 确保description字段有默认值
                            quantity,
                            unit_price,
                            total_price,
                            unit_val,
                            item.get('units_per_box', 1),
                            item.get('packaging'),
                            item.get('notes', '')
                        ))
                
                # 提交事务
                conn.commit()
                
                # 记录刚创建订单的订单项单位，便于调试
                created_order = cls.get_by_id(order_id)
                try:
                    logger.info("新建订单(ID=%s)项单位: %s", order_id, [it.get('unit') for it in created_order.get('items', [])])
                except Exception:
                    logger.debug("无法记录新建订单的项单位")

                return created_order
                
            except Exception as e:
                # 回滚事务
                conn.rollback()
                raise e
    
    @classmethod
    def update(cls, order_id, **kwargs):
        """更新订单及其订单项"""
        items = kwargs.pop('items', None)  # 提取订单项数据
        
        # 更新订单主表
        query = f'''
            UPDATE orders 
            SET {', '.join([f'{key} = ?' for key in kwargs.keys()])}
            WHERE id = ?
        '''
        values = list(kwargs.values()) + [order_id]
        
        from utils.database import get_db_connection
        with get_db_connection() as conn:
            try:
                # 更新订单主表
                conn.execute(query, values)
                
                # 如果提供了订单项数据，则更新订单项
                if items is not None:
                    # 先删除现有的订单项
                    conn.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
                    
                    # 插入新的订单项
                    for item in items:
                        # 计算总价
                        quantity = float(item.get('quantity', 1))
                        unit_price = float(item.get('unit_price', 0))
                        total_price = quantity * unit_price

                        # 如果传入的 unit 为空字符串或 None，则尝试使用产品表中的单位作为回退
                        unit_val = item.get('unit')
                        if not unit_val:
                            try:
                                prod = Product.get_by_id(item.get('product_id')) if item.get('product_id') else None
                                unit_val = prod.get('unit') if prod and prod.get('unit') else '个'
                            except Exception:
                                unit_val = '个'

                        item_query = '''
                            INSERT INTO order_items 
                            (order_id, product_id, description, quantity, unit_price, total_price, unit, units_per_box, packaging, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        '''
                        conn.execute(item_query, (
                            order_id,
                            item.get('product_id'),
                            item.get('description', ''),
                            quantity,
                            unit_price,
                            total_price,
                            unit_val,
                            item.get('units_per_box', 1),
                            item.get('packaging'),
                            item.get('notes', '')
                        ))
                
                conn.commit()

                # 记录更新后订单的订单项单位，便于调试
                updated = cls.get_by_id(order_id)
                try:
                    logger.info("更新订单(ID=%s)后项单位: %s", order_id, [it.get('unit') for it in updated.get('items', [])])
                except Exception:
                    logger.debug("无法记录更新订单的项单位")

                return updated
                
            except Exception as e:
                conn.rollback()
                raise e
    
    @classmethod
    def get_by_id(cls, order_id):
        """
        根据ID获取订单及其关联的产品信息
        
        此方法执行以下操作：
        1. 查询订单主表信息
        2. 加载该订单对应的所有订单项（产品详情）
        3. 处理小箱和大箱的包装信息，转换为嵌套字典结构供前端使用
        
        Args:
            order_id: 订单唯一标识符

        Returns:
            包含订单基本信息、状态及所有商品明细（含包装信息）的字典对象
        """
        query = 'SELECT * FROM orders WHERE id = ?'
        rows = cls.execute_query(query, (order_id,))
        order = serialize_rows(rows)[0] if rows else None
        
        # 如果订单存在，加载其订单项并格式化包装信息
        if order:
            # 获取该订单的所有订单项（即产品信息）
            order['items'] = OrderItem.get_by_order_id(order_id)
            
            # 遍历每个订单项，构建前端友好的箱子信息结构
            for item in order['items']:
                # 小箱信息（如果存在）
                if item.get('small_box_length') is not None:
                    item['smallBox'] = {
                        'length': item['small_box_length'],
                        'width': item['small_box_width'],
                        'height': item['small_box_height'],
                        'weight': item['small_box_weight']
                    }
                
                # 大箱信息（如果存在）
                if item.get('large_box_length') is not None:
                    item['largeBox'] = {
                        'units_per_box': item['large_box_units_per_box'],
                        'length': item['large_box_length'],
                        'width': item['large_box_width'],
                        'height': item['large_box_height'],
                        'weight': item['large_box_weight']
                    }
        
        return order
    
    @classmethod
    def delete(cls, order_id):
        """删除订单"""
        # 检查订单是否存在
        existing = cls.get_by_id(order_id)
        if not existing:
            raise ValueError('订单不存在')
        
        from utils.database import get_db_connection
        from models.transaction import Transaction
        from models.product import Product
        
        with get_db_connection() as conn:
            try:
                # 获取订单项
                order_items = OrderItem.get_by_order_id(order_id)
                
                # 恢复库存并删除相关交易记录
                for item in order_items:
                    product_id = item.get('product_id')
                    quantity = float(item.get('quantity', 0))
                    
                    if product_id and quantity > 0:
                        # 恢复库存（采购订单增加库存，销售订单减少库存）
                        if existing['order_type'] == 'purchase':
                            # 采购订单删除时，如果是已完成状态，则减少库存（原先是增加库存）
                            if existing['status'] == 'completed':
                                Product.update_stock(product_id, -quantity)
                        elif existing['order_type'] == 'sales':
                            # 销售订单删除时，如果是已完成状态，则增加库存（原先是减少库存）
                            if existing['status'] == 'completed':
                                Product.update_stock(product_id, quantity)
                        
                        # 删除相关的交易记录 - 修改这里以确保删除所有相关交易
                        order_number = existing.get('order_number', '')
                        conn.execute(
                            'DELETE FROM transactions WHERE reference_no = ?',
                            (order_number,)
                        )
                
                # 删除订单项
                OrderItem.delete_by_order_id(order_id)
                
                # 删除订单
                query = 'DELETE FROM orders WHERE id = ?'
                cursor = conn.execute(query, (order_id,))
                conn.commit()
                return cursor.rowcount
            except Exception as e:
                conn.rollback()
                raise e

    def delete(self, *args, **kwargs):
        # 删除相关交易记录
        Transaction.objects.filter(order=self).delete()
        
        # 如果订单已完成，则恢复库存数量
        if self.status == 'completed':
            for item in self.items.all():
                product = item.product
                # 修复：已完成的订单删除时应增加库存，而不是减少
                product.quantity += item.quantity
                product.save()
                
                # 创建反向交易记录，记录库存的恢复
                Transaction.objects.create(
                    product=product,
                    transaction_type='incoming',  # 修复：增加库存的交易类型应为incoming
                    quantity=item.quantity,
                    description=f'Reverted from cancelled order {self.order_number}',
                    user=self.created_by,
                    order=self,
                    date=self.updated_at
                )
        
        super().delete(*args, **kwargs)
