"""
Context processors for ecom app
"""

def superadmin_context(request):
    """
    Context processor to provide SuperAdmin check to templates
    """
    is_superadmin = False
    is_manager = False
    
    if request.user.is_authenticated:
        try:
            is_superadmin = hasattr(request.user, 'superadmin') and request.user.superadmin.is_active
        except:
            is_superadmin = False
        try:
            is_manager = request.user.groups.filter(name="Managers").exists()
        except:
            is_manager = False
    
    return {
        'is_superadmin': is_superadmin,
        'is_manager': is_manager,
    }
