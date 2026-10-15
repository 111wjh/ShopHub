from decimal import Decimal
from uuid import uuid4
from rest_framework.permissions import IsAdminUser
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product
from cart.models import Cart, CartItem

from .models import Order, OrderItem
from .serializers import OrderSerializer
from .tasks import cancel_order_if_unpaid
from django.conf import settings

from .services import cancel_pending_order

class OrderCreateView(APIView):
    """从购物车创建订单，并通过行锁防止库存超卖"""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        # 1. 锁定当前用户的购物车
        try:
            cart = Cart.objects.select_for_update().get(
                user=request.user
            )
        except Cart.DoesNotExist:
            return Response(
                {'detail': '购物车不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. 获取购物车商品
        cart_items = list(
            CartItem.objects.select_for_update().filter(
                cart=cart
        ).order_by('product_id')
)

        if not cart_items:
            return Response(
                {'detail': '购物车为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. 按商品 ID 排序并锁定数据库中的商品记录
        product_ids = [item.product_id for item in cart_items]

        products = Product.objects.select_for_update().filter(
            id__in=product_ids
        ).order_by('id')

        product_map = {
            product.id: product
            for product in products
        }

        # 4. 检查商品状态和库存
        for item in cart_items:
            product = product_map.get(item.product_id)

            if product is None or not product.is_active:
                return Response(
                    {'detail': f'商品 ID {item.product_id} 已下架或不存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if item.quantity <= 0:
                return Response(
                    {'detail': '购物车商品数量必须大于 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if item.quantity > product.stock:
                return Response(
                    {'detail': f'{product.name} 库存不足'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 5. 使用数据库中的最新商品价格计算金额
        total_amount = sum(
            (
                product_map[item.product_id].price * item.quantity
                for item in cart_items
            ),
            Decimal('0.00')
        )

        # 6. 创建订单
        order = Order.objects.create(
            user=request.user,
            order_number=uuid4().hex[:20],
            total_amount=total_amount,
            status='pending'
        )

        # 7. 创建订单商品并扣减库存
        for item in cart_items:
            product = product_map[item.product_id]

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=item.quantity,
                subtotal=product.price * item.quantity
            )

            product.stock -= item.quantity
            product.save(update_fields=['stock'])

        # 8. 清空本次下单的购物车商品
        CartItem.objects.filter(
            id__in=[item.id for item in cart_items]
        ).delete()

        # 9. 安排订单超时检查任务

        transaction.on_commit(
            lambda: cancel_order_if_unpaid.apply_async(
                args=[order.id],
                countdown=settings.ORDER_PAYMENT_TIMEOUT_SECONDS,
            )
        )
            

        # 9. 返回订单
        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class OrderListView(APIView):
    """查询订单：管理员查看全部，普通用户只查看自己的"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(
                user=request.user
            )

        orders = orders.prefetch_related(
            'items'
        ).order_by('-created_at')

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)


class OrderDetailView(APIView):
    """查询订单详情：管理员可查看全部，普通用户只能查看自己的"""

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            orders = Order.objects.prefetch_related('items')

            if not request.user.is_staff:
                orders = orders.filter(user=request.user)

            order = orders.get(id=order_id)

        except Order.DoesNotExist:
            return Response(
                {'detail': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)

        return Response(serializer.data)




class OrderCancelView(APIView):
    """取消待支付订单，并安全恢复库存"""

    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        # 先确认订单属于当前用户
        if not Order.objects.filter(
            id=order_id,
            user=request.user,
        ).exists():
            return Response(
                {'detail': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 调用公共取消逻辑
        cancelled = cancel_pending_order(order_id)

        if not cancelled:
            return Response(
                {'detail': '当前订单状态不能取消'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.get(id=order_id)

        return Response(OrderSerializer(order).data)



class OrderPayView(APIView):
    """模拟支付，并防止重复支付"""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        # 锁定当前用户的订单，避免并发修改状态
        try:
            order = Order.objects.select_for_update().get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 只有待支付订单才能支付
        if order.status != 'pending':
            return Response(
                {'detail': '当前订单状态不能支付'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 模拟支付成功
        order.status = 'paid'
        order.save(
            update_fields=['status', 'updated_at']
        )

        serializer = OrderSerializer(order)

        return Response({
            'detail': '模拟支付成功',
            'order': serializer.data
        })


class OrderShipView(APIView):
    """管理员发货"""

    permission_classes = [IsAdminUser]

    @transaction.atomic
    def post(self, request, order_id):
        try:
            order = Order.objects.select_for_update().get(
                id=order_id
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status != 'paid':
            return Response(
                {'detail': '只有已支付订单才能发货'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'shipped'
        order.save(update_fields=['status', 'updated_at'])

        return Response(OrderSerializer(order).data)


class OrderCompleteView(APIView):
    """用户确认收货"""

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        try:
            order = Order.objects.select_for_update().get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status != 'shipped':
            return Response(
                {'detail': '只有已发货订单才能确认收货'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'completed'
        order.save(update_fields=['status', 'updated_at'])

        return Response(OrderSerializer(order).data)