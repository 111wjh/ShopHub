
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    # 查询商品时，展示完整的分类信息
    category = CategorySerializer(read_only=True)

    # 创建或修改商品时，接收分类 ID
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'category_id',
            'name',
            'description',
            'price',
            'stock',
            'image',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('商品价格必须大于 0')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('商品库存不能为负数')
        return value
    
    def validate_image(self, value):
        if not value:
            return value

        # 图片大小不能超过 5 MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                '图片大小不能超过 5 MB'
            )

        # 检查图片文件的真实格式
        from PIL import Image, UnidentifiedImageError

        try:
            value.seek(0)
            image = Image.open(value)

            if image.format not in ('JPEG', 'PNG', 'WEBP'):
                raise serializers.ValidationError(
                    '只允许上传 JPG、PNG、WEBP 格式的图片'
                )

            image.verify()
            value.seek(0)

        except (UnidentifiedImageError, OSError, ValueError):
            raise serializers.ValidationError(
                '请上传有效的 JPG、PNG 或 WEBP 图片'
            )

        return value
