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