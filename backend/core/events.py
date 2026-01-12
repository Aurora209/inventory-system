"""事件系统"""
import logging
from typing import Callable, Dict, List, Any, Type
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import threading
from queue import Queue, Empty
import time

logger = logging.getLogger(__name__)

class EventType(Enum):
    """事件类型枚举"""
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"
    ORDER_CREATED = "order.created"
    ORDER_COMPLETED = "order.completed"
    ORDER_CANCELLED = "order.cancelled"
    TRANSACTION_CREATED = "transaction.created"
    LOW_STOCK_ALERT = "inventory.low_stock"
    SYSTEM_ERROR = "system.error"

@dataclass
class Event:
    """事件基类"""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: datetime = None
    source: str = "system"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class EventHandler:
    """事件处理器基类"""
    
    def handle(self, event: Event):
        """处理事件"""
        raise NotImplementedError

class EventBus:
    """事件总线"""
    
    _instance = None
    _handlers: Dict[EventType, List[Callable]] = {}
    _queue: Queue = Queue()
    _running: bool = False
    _worker_thread: threading.Thread = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """订阅事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        logger.debug("事件处理器注册: %s -> %s", event_type, handler.__name__)
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """取消订阅"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    def publish(self, event: Event):
        """发布事件"""
        logger.debug("发布事件: %s", event.event_type)
        self._queue.put(event)
    
    def publish_sync(self, event: Event):
        """同步发布事件（立即处理）"""
        self._process_event(event)
    
    def start(self):
        """启动事件总线"""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
        logger.info("事件总线启动")
    
    def stop(self):
        """停止事件总线"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        logger.info("事件总线停止")
    
    def _worker(self):
        """事件处理工作线程"""
        while self._running:
            try:
                event = self._queue.get(timeout=1)
                self._process_event(event)
                self._queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logger.error("事件处理错误: %s", e)
    
    def _process_event(self, event: Event):
        """处理单个事件"""
        handlers = self._handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                handler(event)
                logger.debug("事件处理成功: %s -> %s", event.event_type, handler.__name__)
            except Exception as e:
                logger.error(
                    "事件处理失败: %s -> %s: %s", 
                    event.event_type, 
                    handler.__name__, 
                    e
                )

# 全局事件总线实例
event_bus = EventBus()

def event_listener(event_type: EventType):
    """事件监听器装饰器"""
    def decorator(func: Callable):
        event_bus.subscribe(event_type, func)
        return func
    return decorator

# 常用事件处理器
class ProductEventHandlers:
    """产品事件处理器"""
    
    @event_listener(EventType.PRODUCT_CREATED)
    def handle_product_created(event: Event):
        logger.info("产品创建: %s", event.data.get('product_id'))
        # 可以在这里发送通知、更新缓存等
    
    @event_listener(EventType.PRODUCT_UPDATED)
    def handle_product_updated(event: Event):
        logger.info("产品更新: %s", event.data.get('product_id'))
        # 清除相关缓存
        from utils.performance import cache
        cache.delete(f"product_{event.data.get('product_id')}")
    
    @event_listener(EventType.LOW_STOCK_ALERT)
    def handle_low_stock_alert(event: Event):
        product_id = event.data.get('product_id')
        current_stock = event.data.get('current_stock')
        min_stock = event.data.get('min_stock')
        
        logger.warning(
            "低库存预警: 产品ID=%s, 当前库存=%s, 最低库存=%s",
            product_id, current_stock, min_stock
        )
        # 可以在这里发送邮件、短信通知等

class OrderEventHandlers:
    """订单事件处理器"""
    
    @event_listener(EventType.ORDER_COMPLETED)
    def handle_order_completed(event: Event):
        order_id = event.data.get('order_id')
        order_type = event.data.get('order_type')
        
        logger.info("订单完成: ID=%s, 类型=%s", order_id, order_type)
        # 可以在这里触发后续业务流程