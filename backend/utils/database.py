"""优化后的数据库工具"""
import sqlite3
import os
import logging
from contextlib import contextmanager
from typing import Iterator, List, Dict, Any, Optional
from config import config
import threading
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    _instance = None
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self._ensure_database_dir()
        # 初始化连接池
        self._connection_pool = Queue()
        self._pool_lock = threading.Lock()
        self._pool_size = 5
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self._pool_size):
            conn = self._create_connection()
            self._connection_pool.put(conn)
    
    def _create_connection(self):
        """创建新的数据库连接"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
        conn.execute("PRAGMA journal_mode = WAL")  # 启用WAL模式提高并发性能
        return conn
    
    def _ensure_database_dir(self):
        """确保数据库目录存在"""
        config.ensure_data_dir()
    
    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """获取数据库连接（带连接池）"""
        conn = None
        try:
            # 尝试从连接池获取连接
            try:
                conn = self._connection_pool.get_nowait()
            except Empty:
                # 如果连接池为空，创建新连接
                conn = self._create_connection()
            
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error("数据库连接错误: %s", e)
            raise
        finally:
            if conn:
                # 将连接返回到连接池
                try:
                    # 清理连接状态
                    conn.rollback()
                    self._connection_pool.put(conn)
                except:
                    # 如果返回连接池失败，关闭连接
                    conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """执行查询语句"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新语句"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """执行批量操作"""
        with self.get_connection() as conn:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

# 全局数据库管理器实例
db_manager = DatabaseManager()

# 向后兼容的函数
def get_db_connection() -> Iterator[sqlite3.Connection]:
    """获取数据库连接（向后兼容）"""
    return db_manager.get_connection()

def serialize_row(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """将数据库行转换为字典"""
    if row is None:
        return None
    return dict(row)

def serialize_rows(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """将多行数据库记录转换为字典列表"""
    return [serialize_row(row) for row in rows]

def init_database():
    """初始化数据库"""
    from models.category import Category
    from models.product import Product
    from models.bom import BOM
    from models.transaction import Transaction
    from models.order import Order
    from models.order_item import OrderItem
    from models.production import ProductionPlan
    
    # 确保数据目录存在
    config.ensure_data_dir()
    
    logger.info("开始初始化数据库...")
    logger.debug("数据库路径: %s", config.DATABASE_PATH)
    
    # 创建所有表
    tables = [
        Category,
        Product,
        BOM,
        Transaction,
        Order,
        OrderItem,
        ProductionPlan
    ]
    
    for table_class in tables:
        try:
            table_class.create_table()
            logger.debug("创建表: %s", table_class.__name__)
        except Exception as e:
            logger.error("创建表 %s 失败: %s", table_class.__name__, e)
            raise
    
    logger.info("数据库初始化完成")

def get_last_insert_id(conn: sqlite3.Connection) -> Optional[int]:
    """获取最后插入的行ID"""
    try:
        cursor = conn.execute("SELECT last_insert_rowid()")
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except Exception as e:
        logger.error("获取最后插入ID时出错: %s", e)
        return None

# 查询构建工具
class QueryBuilder:
    """安全的SQL查询构建器"""
    
    @staticmethod
    def build_select(
        table: str,
        columns: List[str] = None,
        where: Dict[str, Any] = None,
        order_by: List[str] = None,
        limit: int = None,
        offset: int = None
    ) -> tuple:
        """构建SELECT查询"""
        if columns is None:
            columns = ["*"]
        
        query_parts = [f"SELECT {', '.join(columns)} FROM {table}"]
        params = []
        
        if where:
            where_conditions = []
            for key, value in where.items():
                if value is None:
                    where_conditions.append(f"{key} IS NULL")
                else:
                    where_conditions.append(f"{key} = ?")
                    params.append(value)
            query_parts.append(f"WHERE {' AND '.join(where_conditions)}")
        
        if order_by:
            query_parts.append(f"ORDER BY {', '.join(order_by)}")
        
        if limit is not None:
            query_parts.append(f"LIMIT {limit}")
            if offset is not None:
                query_parts.append(f"OFFSET {offset}")
        
        return " ".join(query_parts), tuple(params)
    
    @staticmethod
    def build_insert(table: str, data: Dict[str, Any]) -> tuple:
        """构建INSERT查询"""
        columns = list(data.keys())
        placeholders = ["?"] * len(columns)
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        return query, tuple(values)
    
    @staticmethod
    def build_update(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> tuple:
        """构建UPDATE查询"""
        set_parts = []
        values = []
        
        for key, value in data.items():
            set_parts.append(f"{key} = ?")
            values.append(value)
        
        where_conditions = []
        for key, value in where.items():
            where_conditions.append(f"{key} = ?")
            values.append(value)
        
        query = f"UPDATE {table} SET {', '.join(set_parts)} WHERE {' AND '.join(where_conditions)}"
        return query, tuple(values)