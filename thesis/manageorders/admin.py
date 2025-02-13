from django.contrib import admin
from .models import Product, Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer_name', 'quantity', 'status', 'order_date')
    search_fields = ('customer_name', 'product__name')