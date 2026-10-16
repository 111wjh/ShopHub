from django.contrib.auth.models import User
from django.db import models

from products.models import Product
from django.db.models import Q

class Order(models.Model):
    """订单"""

    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    order_number = models.CharField(
        max_length=50,
        unique=True
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    paid_at = models.DateTimeField(
    null=True,
    blank=True
)

    
    

    class Meta:
        constraints = [
            models.CheckConstraint(
            condition=Q(total_amount__gte=0),
            name='order_total_amount_nonnegative'
        )
    ]
    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """订单商品"""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(    
        Product,    
        on_delete=models.SET_NULL,    
        null=True,    
        blank=True
)

    product_name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField()

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        constraints = [
        models.CheckConstraint(
            condition=Q(price__gte=0),
            name='order_item_price_nonnegative'
        ),
        models.CheckConstraint(
            condition=Q(subtotal__gte=0),
            name='order_item_subtotal_nonnegative'
        ),
        models.CheckConstraint(
            condition=Q(quantity__gte=1),
            name='order_item_quantity_positive'
        ),
        ]

    def __str__(self):
        return f'{self.product_name} × {self.quantity}'