from models.base import BaseModel
from utils.database import serialize_rows
from collections import defaultdict

class BOM(BaseModel):
    """BOM模型"""
    
    @classmethod
    def create_table(cls):
        """创建BOM表"""
        # 首先检查表是否存在
        check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='bom'"
        result = cls.execute_query(check_query)
        
        if result:
            # 表已存在，检查是否有unit字段
            columns_query = "PRAGMA table_info(bom)"
            columns = cls.execute_query(columns_query)
            has_unit_column = any(column[1] == 'unit' for column in columns) if columns else False
            
            # 如果没有unit字段，则添加该字段
            if not has_unit_column:
                try:
                    alter_query = "ALTER TABLE bom ADD COLUMN unit TEXT DEFAULT '个'"
                    cls.execute_query(alter_query)
                except Exception as e:
                    # 忽略可能的错误，比如字段已存在
                    pass
        else:
            # 表不存在，创建新表
            query = '''
                CREATE TABLE IF NOT EXISTS bom (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    material_id INTEGER NOT NULL,
                    quantity_required DECIMAL(10,3) NOT NULL,
                    unit TEXT DEFAULT '个',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    FOREIGN KEY (material_id) REFERENCES products (id),
                    UNIQUE(product_id, material_id)
                )
            '''
            cls.execute_query(query)
    
    @classmethod
    def get_by_product(cls, product_id):
        """根据产品获取BOM"""
        query = '''
            SELECT b.*, 
                   p.name as product_name,
                   p.sku as product_sku,
                   m.name as material_name,
                   m.sku as material_sku,
                   m.price as material_price,
                   m.quantity as current_stock,
                   m.unit as material_unit
            FROM bom b
            JOIN products p ON b.product_id = p.id
            JOIN products m ON b.material_id = m.id
            WHERE b.product_id = ?
            ORDER BY m.name
        '''
        rows = cls.execute_query(query, (product_id,))
        result = serialize_rows(rows)
        
        for item in result:
            # 优先使用BOM表中的unit字段，如果为空则使用物料的unit字段
            item['unit'] = item.get('unit') or item.get('material_unit', '个')
            item['material_price'] = float(item.get('material_price', 0))
            quantity_required = float(item.get('quantity_required', 0))
            
            # 进行单位换算以正确计算成本
            material_unit = item.get('material_unit', '个')
            bom_unit = item['unit']
            
            # 如果物料单位和BOM单位不同，需要换算价格
            if material_unit.lower() != bom_unit.lower():
                converted_price = cls.convert_unit_price(
                    item['material_price'], 
                    material_unit, 
                    bom_unit
                )
                item['material_price'] = converted_price
                item['item_cost'] = quantity_required * converted_price
            else:
                # 单位相同，直接计算成本
                item['item_cost'] = quantity_required * item['material_price']
                
        return result
    
    @classmethod
    def get_by_product_with_components(cls, product_id, processed_products=None):
        """
        根据产品获取BOM，递归展开所有子组件
        """
        if processed_products is None:
            processed_products = set()
        
        # 防止循环引用
        if product_id in processed_products:
            return []
        
        processed_products.add(product_id)
        
        # 获取直接物料（无论是否为组合产品）
        direct_materials = cls.get_by_product(product_id)
            
        final_bom = {}  # 使用字典来合并相同物料项
        
        for material in direct_materials:
            material_id = material['material_id']
            quantity_required = float(material['quantity_required'])
            unit = material.get('unit', '个')  # 获取单位
            
            # 检查该物料是否有自己的BOM
            sub_bom = cls.get_by_product(material_id)
            
            if sub_bom:
                # 递归获取子组件的展开BOM
                expanded_sub_bom = cls.get_by_product_with_components(material_id, processed_products.copy())
                
                # 将展开的子BOM项乘以当前层的数量要求
                for sub_item in expanded_sub_bom:
                    # 乘以当前层的数量要求
                    sub_quantity = quantity_required * float(sub_item['quantity_required'])
                    
                    # 检查是否已经有相同的物料项
                    key = sub_item['material_id']
                    if key in final_bom:
                        # 如果有，累加数量
                        final_bom[key]['quantity_required'] += sub_quantity
                        
                        # 重新计算成本 - 使用子项的单价和新的数量
                        material_price = float(sub_item.get('material_price', 0))
                        final_bom[key]['item_cost'] = final_bom[key]['quantity_required'] * material_price
                    else:
                        # 创建展开的BOM项
                        material_price = float(sub_item.get('material_price', 0))
                        item_cost = sub_quantity * material_price
                        
                        final_bom[key] = {
                            'id': sub_item.get('id', 0),
                            'product_id': product_id,
                            'material_id': sub_item['material_id'],
                            'material_name': sub_item['material_name'],
                            'material_sku': sub_item['material_sku'],
                            'quantity_required': sub_quantity,
                            'material_price': material_price,
                            'item_cost': item_cost,
                            'material_unit': sub_item.get('material_unit', '个'),
                            'unit': sub_item['unit'],  # 使用子项中的单位
                            'current_stock': sub_item.get('current_stock', 0)
                        }
            else:
                # 如果没有子BOM，直接添加该物料
                key = material['material_id']
                if key in final_bom:
                    # 如果有，累加数量
                    final_bom[key]['quantity_required'] += quantity_required
                    
                    # 重新计算成本 - 使用物料的单价和新的数量
                    material_price = float(material.get('material_price', 0))
                    final_bom[key]['item_cost'] = final_bom[key]['quantity_required'] * material_price
                else:
                    # 直接添加物料项
                    material_price = float(material.get('material_price', 0))
                    item_cost = quantity_required * material_price
                    
                    final_bom[key] = {
                        'id': material.get('id', 0),
                        'product_id': product_id,
                        'material_id': material['material_id'],
                        'material_name': material['material_name'],
                        'material_sku': material['material_sku'],
                        'quantity_required': quantity_required,
                        'material_price': material_price,
                        'item_cost': item_cost,
                        'material_unit': material.get('material_unit', '个'),
                        'unit': material['unit'],  # 使用BOM项中的单位
                        'current_stock': material.get('current_stock', 0)
                    }
        
        # 将字典转换为列表
        expanded_bom = list(final_bom.values())
        return expanded_bom
    
    @staticmethod
    def convert_unit_price(base_price, base_unit, target_unit):
        """单位价格换算方法"""
        # 如果没有基础价格，返回0
        if not base_price:
            return 0.0

        # 如果单位相同，直接返回基础价格
        if base_unit == target_unit:
            return float(base_price)

        # 定义单位换算关系
        unit_conversions = {
            # 重量单位换算 (以g为基准)
            'kg': 1000,    # 1kg = 1000g
            'g': 1,        # 1g = 1g
            'mg': 0.001,   # 1mg = 0.001g

            # 体积单位换算 (以ml为基准)
            'l': 1000,     # 1L = 1000ml
            'ml': 1,       # 1ml = 1ml
            'm³': 1000000, # 1m³ = 1000000ml

            # 其他单位不进行换算
            '个': 1,
            '件': 1,
            '套': 1,
            '箱': 1,
            '包': 1
        }

        # 获取基础单位和目标单位的换算系数
        base_factor = unit_conversions.get(base_unit.lower(), 1)
        target_factor = unit_conversions.get(target_unit.lower(), 1)

        # 如果任一单位不在换算表中，返回原价
        if base_unit.lower() not in unit_conversions or target_unit.lower() not in unit_conversions:
            return float(base_price)

        # 计算换算后的价格
        # 公式: (基础价格 / 基础单位系数) * 目标单位系数
        return (float(base_price) / base_factor) * target_factor
    
    @classmethod
    def get_by_id(cls, bom_id):
        """根据ID获取BOM项"""
        query = '''
            SELECT b.*, 
                   p.name as product_name,
                   m.name as material_name,
                   m.sku as material_sku,
                   m.price as material_price,
                   m.quantity as current_stock,
                   m.unit as material_unit
            FROM bom b
            JOIN products p ON b.product_id = p.id
            JOIN products m ON b.material_id = m.id
            WHERE b.id = ?
        '''
        rows = cls.execute_query(query, (bom_id,))
        result = serialize_rows(rows)
        
        if result:
            item = result[0]
            # 优先使用BOM表中的unit字段，如果为空则使用物料的unit字段
            item['unit'] = item.get('unit') or item.get('material_unit', '个')
            # 确保价格和成本字段为浮点数
            item['material_price'] = float(item.get('material_price', 0))
            if 'item_cost' in item:
                item['item_cost'] = float(item.get('item_cost', 0))
            return item
        
        return None
    
    @classmethod
    def get_by_product_or_material(cls, product_id):
        """根据产品或物料获取BOM使用情况"""
        query = 'SELECT id FROM bom WHERE product_id = ? OR material_id = ?'
        rows = cls.execute_query(query, (product_id, product_id))
        return serialize_rows(rows)
    
    @classmethod
    def create(cls, product_id, material_id, quantity_required, unit='个'):
        """创建BOM项"""
        # 检查是否已存在相同的BOM项
        existing = cls.execute_query(
            'SELECT id FROM bom WHERE product_id = ? AND material_id = ?',
            (product_id, material_id)
        )
        if existing:
            raise ValueError('该物料已存在于BOM中')
        
        # 检查不能添加自己作为物料
        if product_id == material_id:
            raise ValueError('不能添加产品自身作为物料')
        
        # 使用事务确保数据一致性
        with cls.get_db_connection() as conn:
            try:
                query = 'INSERT INTO bom (product_id, material_id, quantity_required, unit) VALUES (?, ?, ?, ?)'
                conn.execute(query, (product_id, material_id, quantity_required, unit))
                conn.commit()
                
                # 获取新创建的BOM项ID并返回完整信息
                cursor = conn.execute("SELECT last_insert_rowid()")
                result = cursor.fetchone()
                if result and result[0] > 0:
                    new_id = result[0]
                    return cls.get_by_id(new_id)
                else:
                    return None
            except Exception as e:
                conn.rollback()
                raise e
    
    @classmethod
    def update(cls, bom_id, quantity_required):
        """更新BOM项"""
        # 检查BOM项是否存在
        existing = cls.get_by_id(bom_id)
        if not existing:
            raise ValueError('BOM项不存在')
        
        query = 'UPDATE bom SET quantity_required = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
        cls.execute_update(query, (quantity_required, bom_id))
        return cls.get_by_id(bom_id)
    
    @classmethod
    def delete(cls, bom_id):
        """删除BOM项"""
        # 检查BOM项是否存在
        existing = cls.get_by_id(bom_id)
        if not existing:
            raise ValueError('BOM项不存在')
        
        query = 'DELETE FROM bom WHERE id = ?'
        return cls.execute_update(query, (bom_id,))