from django.contrib import admin
from .models import UserProfile, PreOrder

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')  # Fields to display in the admin panel
    search_fields = ('user__username', 'phone')  # Enable search by username or phone

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(PreOrder)
