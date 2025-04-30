from django.contrib import admin
from .models import Customer,Product,Orders,Feedback, OrderItem
# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, CustomerAdmin)

class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Product, ProductAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')

class OrderAdmin(admin.ModelAdmin):
        list_display = ('id', 'customer', 'status', 'created_at')
        list_filter = ('status', 'created_at')
        search_fields = ('customer__name', 'customer__email')
        inlines = [OrderItemInline]

admin.site.register(Orders, OrderAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feedback, FeedbackAdmin)