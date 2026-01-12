from models.base import BaseModel
from utils.database import serialize_rows
from datetime import datetime

class Transaction(BaseModel):
    """交易记录模型"""
    
    @classmethod
    def create_table(cls):
        """创建交易记录表"""
        query = '''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_value DECIMAL(10,2) NOT NULL,
                reference_no TEXT,
                customer_supplier TEXT,
                transaction_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        '''
        cls.execute_query(query)
    
    @classmethod
    def get_all(cls, product_id=None, transaction_type=None):
        """获取所有交易记录"""
        query = '''
            SELECT t.*, p.name as product_name, p.sku as product_sku
            FROM transactions t
            JOIN products p ON t.product_id = p.id
            WHERE 1=1
        '''
        params = []
        
        if product_id:
            query += ' AND t.product_id = ?'
            params.append(product_id)
        
        if transaction_type:
            query += ' AND t.transaction_type = ?'
            params.append(transaction_type)
        
        query += ' ORDER BY t.transaction_date DESC, t.created_at DESC'
        
        rows = cls.execute_query(query, params)
        return serialize_rows(rows)
    
    @classmethod
    def get_recent(cls, limit=10):
        """获取最近交易记录"""
        query = '''
            SELECT t.*, p.name as product_name, p.sku as product_sku
            FROM transactions t
            JOIN products p ON t.product_id = p.id
            ORDER BY t.transaction_date DESC, t.created_at DESC
            LIMIT ?
        '''
        rows = cls.execute_query(query, (limit,))
        return serialize_rows(rows)
    
    @classmethod
    def create(cls, product_id, transaction_type, quantity, unit_price, transaction_date, 
               reference_no=None, customer_supplier=None, notes=None):
        """创建交易记录"""
        # 计算总金额
        total_value = float(quantity) * float(unit_price)
        
        # 插入交易记录
        query = '''
            INSERT INTO transactions (product_id, transaction_type, quantity, unit_price, total_value, 
                                   reference_no, customer_supplier, transaction_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cls.execute_update(query, (
            int(product_id), transaction_type, float(quantity), float(unit_price), float(total_value),
            reference_no, customer_supplier, transaction_date, notes
        ))
        
        # 更新产品库存
        from models.product import Product
        quantity_change = float(quantity) if transaction_type == 'in' else -float(quantity)

        # 在入库时，按加权平均成本更新产品单价：
        # new_price = (current_qty * current_price + added_qty * unit_price) / (current_qty + added_qty)
        try:
            if transaction_type == 'in':
                prod = Product.get_by_id(product_id)
                current_qty = float(prod.get('quantity', 0)) if prod else 0.0
                current_price = float(prod.get('price', 0.0)) if prod else 0.0
                added_qty = float(quantity)

                new_qty = current_qty + added_qty
                if new_qty > 0:
                    new_total_value = current_qty * current_price + added_qty * float(unit_price)
                    new_price = new_total_value / new_qty
                    # 先更新库存，再更新价格以保持数据一致性
                    Product.update_stock(product_id, quantity_change)
                    try:
                        Product.update(product_id, price=new_price)
                    except Exception:
                        # 如果更新价格失败，仍然继续（不应阻塞交易创建）
                        pass
                    return cls.get_by_id(cls.get_last_insert_id())

        except Exception:
            # 在任何错误情况下回退到仅更新库存的行为
            pass

        # 默认行为：仅更新库存
        Product.update_stock(product_id, quantity_change)
        
        return cls.get_by_id(cls.get_last_insert_id())
    
    @classmethod
    def get_by_id(cls, transaction_id):
        """根据ID获取交易记录"""
        query = '''
            SELECT t.*, p.name as product_name, p.sku as product_sku
            FROM transactions t
            JOIN products p ON t.product_id = p.id
            WHERE t.id = ?
        '''
        rows = cls.execute_query(query, (transaction_id,))
        return serialize_rows(rows)[0] if rows else None
    
    @classmethod
    def get_today_stats(cls):
        """获取今日交易统计"""
        today = datetime.now().date().isoformat()
        
        query_in = '''
            SELECT COALESCE(SUM(quantity), 0) as total 
            FROM transactions 
            WHERE transaction_type = 'in' AND transaction_date = ?
        '''
        result_in = cls.execute_query(query_in, (today,))
        today_incoming = int(result_in[0][0]) if result_in and len(result_in) > 0 else 0
        
        query_out = '''
            SELECT COALESCE(SUM(quantity), 0) as total 
            FROM transactions 
            WHERE transaction_type = 'out' AND transaction_date = ?
        '''
        result_out = cls.execute_query(query_out, (today,))
        today_outgoing = int(result_out[0][0]) if result_out and len(result_out) > 0 else 0
        
        return today_incoming, today_outgoing
