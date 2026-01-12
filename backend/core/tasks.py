"""任务队列系统"""
import logging
import threading
from typing import Callable, Dict, Any, Optional
from queue import PriorityQueue
from enum import IntEnum
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TaskPriority(IntEnum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class TaskStatus:
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    """任务类"""
    
    def __init__(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        retries: int = 0,
        timeout: int = None,
        scheduled_time: datetime = None
    ):
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.retries = retries
        self.timeout = timeout
        self.scheduled_time = scheduled_time or datetime.now()
        
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.attempts = 0
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
    
    def __lt__(self, other):
        # 用于优先级队列比较
        if self.priority != other.priority:
            return self.priority > other.priority  # 优先级高的先执行
        return self.scheduled_time < other.scheduled_time
    
    def execute(self):
        """执行任务"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
        self.attempts += 1
        
        try:
            if self.timeout:
                # 带超时的执行
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("任务执行超时")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.timeout)
                
                try:
                    self.result = self.func(*self.args, **self.kwargs)
                finally:
                    signal.alarm(0)
            else:
                # 普通执行
                self.result = self.func(*self.args, **self.kwargs)
            
            self.status = TaskStatus.COMPLETED
            logger.debug("任务执行成功: %s", self.func.__name__)
            
        except Exception as e:
            self.error = str(e)
            if self.attempts <= self.retries:
                self.status = TaskStatus.PENDING
                logger.warning("任务执行失败，准备重试: %s, 错误: %s", self.func.__name__, e)
            else:
                self.status = TaskStatus.FAILED
                logger.error("任务执行失败: %s, 错误: %s", self.func.__name__, e)
        
        finally:
            self.completed_at = datetime.now()

class TaskQueue:
    """任务队列"""
    
    _instance = None
    _queue: PriorityQueue = None
    _workers: list = []
    _running: bool = False
    _worker_count: int = 3
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._queue = PriorityQueue()
        return cls._instance
    
    def enqueue(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        retries: int = 0,
        timeout: int = None,
        delay: int = 0
    ) -> Task:
        """添加任务到队列"""
        scheduled_time = datetime.now() + timedelta(seconds=delay)
        
        task = Task(
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            retries=retries,
            timeout=timeout,
            scheduled_time=scheduled_time
        )
        
        self._queue.put(task)
        logger.debug("任务入队: %s, 优先级=%s", func.__name__, priority)
        
        return task
    
    def start(self, worker_count: int = None):
        """启动任务队列"""
        if self._running:
            return
        
        self._running = True
        self._worker_count = worker_count or self._worker_count
        
        for i in range(self._worker_count):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{i}",
                daemon=True
            )
            worker.start()
            self._workers.append(worker)
        
        logger.info("任务队列启动: 工作线程数=%s", self._worker_count)
    
    def stop(self):
        """停止任务队列"""
        self._running = False
        for worker in self._workers:
            worker.join(timeout=5)
        self._workers.clear()
        logger.info("任务队列停止")
    
    def _worker_loop(self):
        """工作线程循环"""
        while self._running:
            try:
                task = self._queue.get(timeout=1)
                
                # 检查任务是否应该执行
                if datetime.now() < task.scheduled_time:
                    # 重新放回队列
                    self._queue.put(task)
                    time.sleep(0.1)
                    continue
                
                # 执行任务
                task.execute()
                self._queue.task_done()
                
            except Exception as e:
                logger.error("工作线程错误: %s", e)
                time.sleep(1)

# 全局任务队列实例
task_queue = TaskQueue()

def background_task(
    priority: TaskPriority = TaskPriority.NORMAL,
    retries: int = 0,
    timeout: int = None,
    delay: int = 0
):
    """后台任务装饰器"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            return task_queue.enqueue(
                func=func,
                args=args,
                kwargs=kwargs,
                priority=priority,
                retries=retries,
                timeout=timeout,
                delay=delay
            )
        return wrapper
    return decorator

# 常用后台任务
class InventoryTasks:
    """库存相关任务"""
    
    @staticmethod
    @background_task(priority=TaskPriority.LOW)
    def update_product_statistics(product_id: int):
        """更新产品统计信息（低优先级后台任务）"""
        from models.product import Product
        from models.transaction import Transaction
        
        product = Product.get_by_id(product_id)
        if not product:
            return
        
        # 计算最近30天的交易统计
        # 这里可以实现复杂的统计计算
        logger.debug("更新产品统计: ID=%s", product_id)
    
    @staticmethod
    @background_task(priority=TaskPriority.HIGH, retries=3)
    def process_low_stock_notifications():
        """处理低库存通知（高优先级，可重试）"""
        from models.product import Product
        from core.events import event_bus, Event, EventType
        
        low_stock_products = Product.get_low_stock_products()
        
        for product in low_stock_products:
            event = Event(
                event_type=EventType.LOW_STOCK_ALERT,
                data={
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'current_stock': product['quantity'],
                    'min_stock': product['min_stock']
                }
            )
            event_bus.publish(event)

class ReportTasks:
    """报表相关任务"""
    
    @staticmethod
    @background_task(priority=TaskPriority.NORMAL, timeout=300)
    def generate_inventory_report(start_date: str, end_date: str):
        """生成库存报表（长时间运行任务）"""
        import pandas as pd
        from models.product import Product
        from models.transaction import Transaction
        
        logger.info("开始生成库存报表: %s 到 %s", start_date, end_date)
        
        # 模拟长时间运行
        time.sleep(10)
        
        # 这里可以实现复杂的报表生成逻辑
        logger.info("库存报表生成完成")
        
        return {
            'status': 'completed',
            'report_url': f'/reports/inventory_{start_date}_{end_date}.xlsx'
        }