from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from products.models import Product

from .models import Cart, CartItem
from .serializers import CartSerializer

def parse_positive_integer(value):
    """将输入校验为严格的正整数，不接受小数和布尔值。"""
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value if value > 0 else None

    if isinstance(value, str):
        value = value.strip()
        if value.isdigit():
            number = int(value)
            return number if number > 0 else None

    return None

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        serializer = CartSerializer(cart)

        return Response(serializer.data)




class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response(
                {'detail': 'product_id 是必填项'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 校验商品 ID，拒绝小数、布尔值和非数字字符串
        product_id = parse_positive_integer(product_id)
        if product_id is None:
            return Response(
                {'detail': 'product_id 必须是正整数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        quantity = parse_positive_integer(quantity)
        if quantity is None:
            return Response(
                {'detail': 'quantity 必须是正整数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 锁定商品记录，避免并发修改商品库存时产生冲突
        try:
            product = Product.objects.select_for_update().get(
                id=product_id,
                is_active=True
            )
        except Product.DoesNotExist:
            return Response(
                {'detail': '商品不存在或已下架'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 创建或获取当前用户的购物车，并锁定购物车记录
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )
        cart = Cart.objects.select_for_update().get(
            id=cart.id
        )

        # 查找购物车中是否已有该商品
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()

        new_quantity = quantity
        if cart_item:
            new_quantity += cart_item.quantity

        # 校验添加后的商品总数量
        if new_quantity > product.stock:
            return Response(
                {'detail': '库存不足'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 更新已有商品或创建新商品
        if cart_item:
            cart_item.quantity = new_quantity
            cart_item.save(update_fields=['quantity', 'updated_at'])
        else:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )

        serializer = CartSerializer(cart)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )






class CartItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'detail': '购物车商品不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get('quantity')

        if quantity is None:
            return Response(
                {'detail': 'quantity 是必填项'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 校验数量格式
        quantity = parse_positive_integer(quantity)

        if quantity is None:
            return Response(
            {'detail': 'quantity 必须是正整数'},
            status=status.HTTP_400_BAD_REQUEST
    )

        # 校验商品是否仍然在售
        if not cart_item.product.is_active:
            return Response(
                {'detail': '该商品已下架'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 校验库存
        if quantity > cart_item.product.stock:
            return Response(
                {'detail': '库存不足'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart_item.cart)

        return Response(serializer.data)


class CartItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'detail': '购物车商品不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = cart_item.cart
        cart_item.delete()

        serializer = CartSerializer(cart)

        return Response(serializer.data)