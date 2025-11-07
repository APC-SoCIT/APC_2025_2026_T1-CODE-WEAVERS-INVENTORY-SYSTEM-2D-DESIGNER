from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Customer, Product, Orders, Feedback, OrderItem, Address, ChatSession, ChatMessage, ChatbotKnowledge, SuperAdmin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['region', 'province', 'city_municipality', 'barangay', 'street', 'postal_code']
    search_fields = ['region', 'province', 'city_municipality', 'barangay', 'street', 'postal_code']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile', 'region_name', 'province_name', 'citymun_name', 'barangay_name']
    list_filter = ['region', 'province', 'citymun', 'barangay']
    search_fields = ['user__first_name', 'user__last_name', 'region', 'province', 'citymun', 'barangay', 'street_address']

    def region_name(self, obj):
        from ecom.utils import get_region_name
        return get_region_name(obj.region) if obj.region else ''
    region_name.short_description = 'Region'

    def province_name(self, obj):
        from ecom.utils import get_province_name
        return get_province_name(obj.province) if obj.province else ''
    province_name.short_description = 'Province'

    def citymun_name(self, obj):
        from ecom.utils import get_citymun_name
        return get_citymun_name(obj.citymun) if obj.citymun else ''
    citymun_name.short_description = 'City/Municipality'

    def barangay_name(self, obj):
        from ecom.utils import get_barangay_name
        return get_barangay_name(obj.barangay) if obj.barangay else ''
    barangay_name.short_description = 'Barangay'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'size']
    list_filter = ['size']
    search_fields = ['name', 'description']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')
    extra = 0  # Don't show extra empty forms
    can_delete = False  # Prevent deletion of order items

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_ref', 'customer', 'status', 'payment_method', 'address', 
        'mobile', 'email', 'order_date', 'created_at', 'estimated_delivery_date'
    )
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('order_ref', 'customer__user__first_name', 'customer__user__last_name', 'mobile', 'email', 'address')
    inlines = [OrderItemInline]
    
    # Make customer order details read-only to protect order integrity
    readonly_fields = (
        'created_at', 'updated_at', 'customer', 'email', 'address', 'mobile', 
        'order_date', 'payment_method', 'transaction_id', 'order_ref', 
        'delivery_fee', 'delivery_proof_photo', 'customer_received_at',
        'cancellation_reason', 'cancellation_requested_at', 'cancellation_approved_by',
        'cancellation_approved_at', 'refund_processed', 'refund_amount', 
        'refund_processed_at', 'refund_processed_by'
    )
    
    # Fields that can be edited by admin (operational fields only)
    fields = (
        # Read-only customer and order information
        ('order_ref', 'customer', 'order_date'),
        ('email', 'mobile'),
        ('address',),
        ('payment_method', 'transaction_id'),
        ('delivery_fee',),
        
        # Editable operational fields
        ('status', 'estimated_delivery_date'),
        ('tracking_url',),
        ('notes',),
        
        # Cancellation information (read-only)
        ('cancellation_status', 'cancellation_reason'),
        ('cancellation_requested_at', 'cancellation_approved_by', 'cancellation_approved_at'),
        ('cancellation_admin_notes',),
        
        # Delivery tracking (read-only customer proof, editable admin fields)
        ('delivery_proof_photo', 'customer_received_at'),
        
        # Refund information (read-only)
        ('refund_processed', 'refund_amount', 'refund_processed_at', 'refund_processed_by'),
        
        # Timestamps (read-only)
        ('created_at', 'updated_at'),
    )
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of orders to maintain data integrity"""
        return False

admin.site.register(Orders, OrderAdmin)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']
    search_fields = ['name', 'feedback']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'customer', 'handover_status', 'created_at', 'is_active']
    list_filter = ['handover_status', 'is_active', 'created_at']
    search_fields = ['session_id', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'admin_user')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'admin_user')


@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['category', 'question', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer', 'keywords']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SuperAdmin)
class SuperAdminAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'position', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id', 'department', 'position']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'employee_id')
        }),
        ('Work Details', {
            'fields': ('department', 'position', 'phone')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Customize admin site headers
admin.site.site_header = "WorksTeamWear Administration"
admin.site.site_title = "WorksTeamWear Admin Portal"
admin.site.index_title = "Welcome to WorksTeamWear Administration"

# --- Restrict User admin for non-superusers (Managers/Staff) ---
try:
    admin.site.unregister(User)
except Exception:
    pass


class RestrictedUserAdmin(BaseUserAdmin):
    """
    Custom User admin:
    - Managers cannot view/edit SuperAdmin users (is_superuser=True)
    - Managers can only assign the 'Staff' group to users
    - Hide superuser-only fields for non-superusers
    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # If Manager (or any non-superuser), hide superuser accounts
        if request.user.groups.filter(name="Managers").exists():
            return qs.exclude(is_superuser=True)
        return qs

    def has_view_permission(self, request, obj=None):
        allowed = super().has_view_permission(request, obj)
        if not allowed:
            return False
        if obj and obj.is_superuser and not request.user.is_superuser:
            # Block Managers/Staff from viewing SuperAdmin user details
            return False
        return True

    def has_change_permission(self, request, obj=None):
        allowed = super().has_change_permission(request, obj)
        if not allowed:
            return False
        if obj and obj.is_superuser and not request.user.is_superuser:
            # Block Managers/Staff from editing SuperAdmin user details
            return False
        return True

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Limit group assignment for non-superusers to 'Staff' only
        if db_field.name == "groups" and not request.user.is_superuser:
            if request.user.groups.filter(name="Managers").exists():
                kwargs["queryset"] = Group.objects.filter(name="Staff")
            else:
                kwargs["queryset"] = Group.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets
        # Remove superuser-only fields for Managers/Staff
        filtered = []
        for name, opts in fieldsets:
            opts = dict(opts)
            fields = opts.get("fields")
            if fields:
                opts["fields"] = tuple(
                    f for f in fields if f not in ("is_superuser", "user_permissions")
                )
            filtered.append((name, opts))
        return tuple(filtered)

    def get_add_fieldsets(self, request):
        add_fieldsets = super().get_add_fieldsets(request)
        if request.user.is_superuser:
            return add_fieldsets
        # Ensure 'is_superuser' cannot be set during add
        filtered = []
        for name, opts in add_fieldsets:
            opts = dict(opts)
            fields = opts.get("fields")
            if fields:
                opts["fields"] = tuple(
                    f for f in fields if f not in ("is_superuser", "user_permissions")
                )
            filtered.append((name, opts))
        return tuple(filtered)


admin.site.register(User, RestrictedUserAdmin)
