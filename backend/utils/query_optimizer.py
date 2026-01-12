"""数据库查询优化工具"""
import logging
from typing import List, Dict, Any, Optional, Union
from functools import wraps
from models.base import BaseModel
from utils.performance import measure_performance, cache

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """查询优化器"""
    
    @staticmethod
    @measure_performance("database_query")
    def optimized_get_all(
        model_class: BaseModel,
        filters: Dict[str, Any] = None,
        order_by: List[str] = None,
        limit: int = None,
        offset: int = None,
        include_related: List[str] = None
    ) -> List[Dict[str, Any]]:
        """优化的获取所有记录方法"""
        base_query = f"SELECT * FROM {model_class.TABLE_NAME}"
        params = []
        
        # 构建WHERE条件
        where_conditions = []
        if filters:
            for key, value in filters.items():
                if value is None:
                    where_conditions.append(f"{key} IS NULL")
                else:
                    where_conditions.append(f"{key} = ?")
                    params.append(value)
        
        if where_conditions:
            base_query += f" WHERE {' AND '.join(where_conditions)}"
        
        # 排序
        if order_by:
            base_query += f" ORDER BY {', '.join(order_by)}"
        
        # 分页
        if limit is not None:
            base_query += f" LIMIT {limit}"
            if offset is not None:
                base_query += f" OFFSET {offset}"
        
        # 执行查询
        results = model_class.execute_query(base_query, tuple(params))
        
        # 处理关联数据
        if include_related and results:
            results = QueryOptimizer._include_related_data(
                model_class, results, include_related
            )
        
        return results
    
    @staticmethod
    def _include_related_data(
        model_class: BaseModel,
        results: List[Dict[str, Any]],
        include_related: List[str]
    ) -> List[Dict[str, Any]]:
        """包含关联数据"""
        # 这里可以根据模型类实现具体的关联数据加载
        # 例如：对于产品，可以加载分类信息等
        
        # 这是一个通用实现，具体模型可以重写此方法
        for result in results:
            for relation in include_related:
                # 这里需要根据具体的关系来实现
                # 例如：如果 relation 是 'category'，则加载分类信息
                result[f'{relation}_info'] = None
        
        return results
    
    @staticmethod
    @cache(ttl=60)  # 缓存1分钟
    def get_with_cache(
        model_class: BaseModel,
        record_id: int,
        include_related: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """带缓存的获取单个记录方法"""
        return model_class.get_by_id(record_id)

class BatchProcessor:
    """批量处理器"""
    
    @staticmethod
    def batch_insert(
        model_class: BaseModel,
        data_list: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """批量插入数据"""
        if not data_list:
            return 0
        
        total_inserted = 0
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            inserted = BatchProcessor._insert_batch(model_class, batch)
            total_inserted += inserted
        
        logger.info("批量插入完成: 总数=%s, 批次大小=%s", total_inserted, batch_size)
        return total_inserted
    
    @staticmethod
    def _insert_batch(model_class: BaseModel, batch: List[Dict[str, Any]]) -> int:
        """插入单个批次"""
        if not batch:
            return 0
        
        # 获取所有字段
        all_keys = set()
        for item in batch:
            all_keys.update(item.keys())
        
        columns = list(all_keys)
        placeholders = ['?' for _ in columns]
        
        query = f"""
            INSERT INTO {model_class.TABLE_NAME} 
            ({', '.join(columns)}) 
            VALUES ({', '.join(placeholders)})
        """
        
        # 准备参数
        params_list = []
        for item in batch:
            params = [item.get(col) for col in columns]
            params_list.append(tuple(params))
        
        try:
            return model_class.execute_many(query, params_list)
        except Exception as e:
            logger.error("批量插入失败: %s", e)
            # 回退到逐条插入
            return BatchProcessor._insert_individual(model_class, batch)
    
    @staticmethod
    def _insert_individual(model_class: BaseModel, batch: List[Dict[str, Any]]) -> int:
        """逐条插入（回退方法）"""
        inserted_count = 0
        
        for item in batch:
            try:
                model_class.create(**item)
                inserted_count += 1
            except Exception as e:
                logger.error("单条插入失败: %s, 数据: %s", e, item)
        
        return inserted_count

class IndexManager:
    """索引管理器"""
    
    @staticmethod
    def create_indexes():
        """创建必要的索引"""
        indexes = {
            'products': [
                'CREATE INDEX IF NOT EXISTS idx_products_sku ON products (sku)',
                'CREATE INDEX IF NOT EXISTS idx_products_category ON products (category_id)',
                'CREATE INDEX IF NOT EXISTS idx_products_name ON products (name)',
                'CREATE INDEX IF NOT EXISTS idx_products_composite ON products (is_composite)'
            ],
            'categories': [
                'CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories (parent_id)',
                'CREATE INDEX IF NOT EXISTS idx_categories_level ON categories (level)'
            ],
            'transactions': [
                'CREATE INDEX IF NOT EXISTS idx_transactions_product ON transactions (product_id)',
                'CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (transaction_date)',
                'CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions (transaction_type)'
            ],
            'orders': [
                'CREATE INDEX IF NOT EXISTS idx_orders_number ON orders (order_number)',
                'CREATE INDEX IF NOT EXISTS idx_orders_type ON orders (order_type)',
                'CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status)',
                'CREATE INDEX IF NOT EXISTS idx_orders_date ON orders (order_date)'
            ],
            'order_items': [
                'CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items (order_id)',
                'CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items (product_id)'
            ],
            'bom': [
                'CREATE INDEX IF NOT EXISTS idx_bom_product ON bom (product_id)',
                'CREATE INDEX IF NOT EXISTS idx_bom_material ON bom (material_id)'
            ]
        }
        
        for table, table_indexes in indexes.items():
            for index_query in table_indexes:
                try:
                    BaseModel.execute_query(index_query)
                    logger.debug("创建索引: %s", index_query)
                except Exception as e:
                    logger.warning("创建索引失败 %s: %s", index_query, e)