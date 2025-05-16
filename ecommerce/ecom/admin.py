from django.contrib import admin
from .models import Customer,Product,Orders,Feedback, OrderItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'country', 'city', 'mobile']
    list_filter = ['country', 'city']
    search_fields = ['user__first_name', 'user__last_name', 'city', 'street_address']
    readonly_fields = ['get_full_address']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'size']
    list_filter = ['size']
    search_fields = ['name', 'description']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')

class OrderAdmin(admin.ModelAdmin):
        list_display = ('id', 'customer', 'status', 'created_at')
        list_filter = ('status', 'created_at')
        search_fields = ('customer__name', 'customer__email')
        inlines = [OrderItemInline]

admin.site.register(Orders, OrderAdmin)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']
    search_fields = ['name', 'feedback']