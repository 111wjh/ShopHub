
from django.urls import path

from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    CategoryListView
)


urlpatterns = [
    # 商品列表
    path('', ProductListView.as_view(), name='product-list'),

    # 商品详情
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # 创建商品
    path('create/', ProductCreateView.as_view(), name='product-create'),

    # 修改商品
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),

    # 删除商品
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    # 商品分类列表
    path('categories/', CategoryListView.as_view(), name='category-list'),
]
