from models.base import BaseModel
from utils.database import serialize_rows
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class Category(BaseModel):
    """分类模型"""
    
    @classmethod
    def create_table(cls):
        """创建分类表"""
        # 创建主表
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories (id)
            )
        '''
        cls.execute_query(create_table_query)

        # 为 parent_id 创建索引以提高查询性能
        create_index_query = 'CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories (parent_id)'
        cls.execute_query(create_index_query)

        # 为顶级分类（level=1）的名称创建唯一索引，防止重复
        create_unique_index_query = 'CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_name_level ON categories (name, level) WHERE level = 1'
        cls.execute_query(create_unique_index_query)
    
    @classmethod
    def get_all_flat(cls):
        """获取所有分类（扁平结构）"""
        query = 'SELECT * FROM categories ORDER BY level, name'
        rows = cls.execute_query(query)
        return serialize_rows(rows)
    
    @classmethod
    def get_all_tree(cls):
        """获取所有分类（树状结构）"""
        categories = cls.get_all_flat()
        
        # 构建树状结构
        root_categories = [cat for cat in categories if cat['level'] == 1]
        child_categories = [cat for cat in categories if cat['level'] == 2]
        
        for root in root_categories:
            root['children'] = [cat for cat in child_categories if cat['parent_id'] == root['id']]
        
        return root_categories
    
    @classmethod
    def get_by_id(cls, category_id):
        """根据ID获取分类"""
        query = 'SELECT * FROM categories WHERE id = ?'
        rows = cls.execute_query(query, (category_id,))
        return serialize_rows(rows)[0] if rows else None
    
    @classmethod
    def create(cls, name, parent_id=None, level=1):
        """创建分类"""
        try:
            # 检查是否已存在相同名称和层级的分类
            if level == 1:
                existing = cls.execute_query(
                    'SELECT id FROM categories WHERE name = ? AND level = ?',
                    (name, level)
                )
            else:
                existing = cls.execute_query(
                    'SELECT id FROM categories WHERE name = ? AND parent_id = ? AND level = ?',
                    (name, parent_id, level)
                )
            
            if existing:
                raise ValueError('同级分类名称已存在')
            
            query = '''
                INSERT INTO categories (name, parent_id, level)
                VALUES (?, ?, ?)
            '''
            
            # 使用数据库连接上下文管理器确保操作在同一连接中完成
            with cls.get_db_connection() as conn:
                cursor = conn.execute(query, (name, parent_id, level))
                conn.commit()
                
                # 获取最后插入的ID
                cursor = conn.execute("SELECT last_insert_rowid()")
                result = cursor.fetchone()
                if result:
                    if isinstance(result, (list, tuple)):
                        category_id = int(result[0])
                    elif hasattr(result, '__getitem__'):
                        category_id = int(result[0])
                    else:
                        category_id = int(result)
                else:
                    category_id = None
                    
                if category_id is None or category_id <= 0:
                    raise ValueError('创建分类失败，无法获取分类ID')
                
                # 直接查询新创建的分类数据
                result_query = '''
                    SELECT id, name, parent_id, level, 
                           created_at, updated_at 
                    FROM categories 
                    WHERE id = ?
                '''
                result = conn.execute(result_query, (category_id,)).fetchall()
                
                if not result:
                    raise ValueError('创建分类失败，无法查询到刚创建的分类')
                
                # 返回新创建的分类
                category_data = serialize_rows(result)[0]
                return category_data
            
        except Exception as e:
            logger.error("创建分类失败: %s", str(e))
            raise
    
    @classmethod
    def update(cls, category_id, name):
        """更新分类"""
        query = 'UPDATE categories SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
        cls.execute_update(query, (name, category_id))
        return cls.get_by_id(category_id)
    
    @classmethod
    def delete(cls, category_id):
        """删除分类"""
        # 检查是否有子分类
        children = cls.execute_query('SELECT id FROM categories WHERE parent_id = ?', (category_id,))
        if children:
            raise ValueError('该分类下有子分类，无法删除')
        
        # 检查是否有产品使用该分类
        from models.product import Product
        products = Product.get_by_category(category_id)
        if products:
            raise ValueError('有产品使用该分类，无法删除')
        
        query = 'DELETE FROM categories WHERE id = ?'
        return cls.execute_update(query, (category_id,))

    # 添加获取数据库连接的方法
    @classmethod
    @contextmanager
    def get_db_connection(cls):
        """获取数据库连接"""
        from utils.database import get_db_connection
        with get_db_connection() as conn:
            yield conn