from django.urls import path

from .views import (
    CartView,
    CartAddView,
    CartItemUpdateView,
    CartItemDeleteView,
)


urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', CartAddView.as_view(), name='cart-add'),

    path(
        'item/<int:item_id>/',
        CartItemUpdateView.as_view(),
        name='cart-item-update'
    ),

    path(
        'item/<int:item_id>/delete/',
        CartItemDeleteView.as_view(),
        name='cart-item-delete'
    ),
]