from django.urls import path

from .views import (
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    OrderCancelView,
    OrderPayView,
    OrderShipView,
    OrderCompleteView,
)


urlpatterns = [
    path(
        'create/',
        OrderCreateView.as_view(),
        name='order-create'
    ),

    path(
        '',
        OrderListView.as_view(),
        name='order-list'
    ),

    path(
        '<int:order_id>/cancel/',
        OrderCancelView.as_view(),
        name='order-cancel'
    ),

    path(
        '<int:order_id>/',
        OrderDetailView.as_view(),
        name='order-detail'
    ),
    path('<int:order_id>/pay/',    
        OrderPayView.as_view(),    
        name='order-pay'
    ),
    path('<int:order_id>/ship/',    
        OrderShipView.as_view(),    
        name='order-ship'
    ),
    path('<int:order_id>/complete/',    
        OrderCompleteView.as_view(),    
        name='order-complete'
),
]