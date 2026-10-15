
from django.db import transaction

from products.models import Product
from .models import Order, OrderItem


@transaction.atomic
def cancel_pending_order(order_id):
    """取消待支付订单，并安全恢复库存。"""

    # 锁定订单，避免支付和取消同时修改状态
    try:
        order = Order.objects.select_for_update().get(
            id=order_id
        )
    except Order.DoesNotExist:
        return False

    # 只有待支付订单可以取消
    if order.status != 'pending':
        return False

    # 获取订单商品
    items = list(
        OrderItem.objects.filter(
            order=order
        ).order_by('product_id')
    )

    # 按商品 ID 排序并锁定商品记录
    product_ids = sorted({
        item.product_id
        for item in items
        if item.product_id is not None
    })

    products = Product.objects.select_for_update().filter(
        id__in=product_ids
    ).order_by('id')

    product_map = {
        product.id: product
        for product in products
    }

    # 恢复库存
    for item in items:
        product = product_map.get(item.product_id)

        if product is None:
            continue

        product.stock += item.quantity
        product.save(update_fields=['stock'])

    # 更新订单状态
    order.status = 'cancelled'
    order.save(update_fields=['status', 'updated_at'])

    return True
