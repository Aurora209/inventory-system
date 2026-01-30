from django.db import models
from django.contrib.auth.models import User
from .product import Product
from .transaction import Transaction


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=100, unique=True)
    supplier_name = models.CharField(max_length=200)
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.supplier_name}"

    def delete(self, *args, **kwargs):
        # 获取所有相关交易记录以便稍后删除
        related_transactions = Transaction.objects.filter(order=self)
        
        # 如果订单已完成，则在删除交易前恢复库存数量
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
        
        # 删除相关交易记录
        related_transactions.delete()
        
        super().delete(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"