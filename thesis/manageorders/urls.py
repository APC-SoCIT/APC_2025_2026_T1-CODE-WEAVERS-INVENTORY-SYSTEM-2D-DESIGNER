from django.urls import path
from .views import order_list, add_order, edit_order

urlpatterns = [
    path('orders/', order_list, name='order_list'),
    path('orders/add/', add_order, name='add_order'),
    path('orders/edit/<int:order_id>/', edit_order, name='edit_order'),
]