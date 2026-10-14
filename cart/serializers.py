
from decimal import Decimal

from rest_framework import serializers

from .models import Cart, CartItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'quantity',
            'subtotal',
            'created_at',
            'updated_at',
        ]

    def get_subtotal(self, obj):
        if obj.product is None:
            return Decimal('0.00')

        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'items',
            'total_amount',
            'created_at',
            'updated_at',
        ]

    def get_total_amount(self, obj):
        total = Decimal('0.00')

        for item in obj.items.all():
            if item.product is not None:
                total += item.product.price * item.quantity

        return total
