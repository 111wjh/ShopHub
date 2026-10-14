
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.db.models import Q

# 商品列表：所有人都可以查看
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    
    def get_queryset(self):
        # 管理员可以通过后台参数查看全部商品
        if (
            self.request.user.is_authenticated
            and self.request.user.is_staff
            and self.request.query_params.get('manage') == 'true'
        ):
            queryset = Product.objects.all()
        else:
            # 普通前台只展示已上架商品
            queryset = Product.objects.filter(is_active=True)

        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')

        if search:
            search = search.strip()
            if search:
                queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
        )

        
        if category is not None and category.strip():
            if not category.isdigit():
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    ' category': '分类 ID 必须是正整数'
                })

            queryset = queryset.filter(category_id=int(category))

        return queryset


# 商品详情：所有人都可以查看
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # 前台只允许查看已上架商品
        return Product.objects.filter(is_active=True)


# 创建商品：仅管理员
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


# 修改商品：仅管理员
class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


# 删除商品：仅管理员
class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]



# 商品分类列表：所有人都可以查看
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
