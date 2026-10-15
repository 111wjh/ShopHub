
from celery import shared_task

from .services import cancel_pending_order


@shared_task
def cancel_order_if_unpaid(order_id):
    """自动取消超时且仍未支付的订单。"""
    cancelled = cancel_pending_order(order_id)

    if cancelled:
        return f'Order {order_id} cancelled due to timeout.'

    return f'Order {order_id} was not cancelled.'
