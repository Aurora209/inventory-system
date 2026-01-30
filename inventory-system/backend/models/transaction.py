from django.db import models
from django.contrib.auth.models import User
from .product import Product
from .order import Order


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')

    def __str__(self):
        return f"{self.transaction_type.title()} - {self.product.name} ({self.quantity})"