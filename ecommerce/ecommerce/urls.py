from django.contrib import admin
from django.urls import path
from ecom import views
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic import RedirectView
from ecom.views import manage_inventory, update_stock 
from ecom.views import delete_inventory, edit_inventory, bulk_update_orders
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/', admin.site.urls),
    path('manage-inventory', manage_inventory, name='manage-inventory'),
    path('update-stock/<int:item_id>/', update_stock, name='update-stock'),
    path('',views.home_view,name=''),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout/', LogoutView.as_view(template_name='ecom/logout.html', next_page='customerlogin'), name='logout'),
    path('about', views.aboutus_view, name='about'),
    path('contactus', views.contactus_view,name='contactus'),
    path('search', views.search_view,name='search'),
    path('send-feedback', views.send_feedback_view,name='send-feedback'),
    path('view-feedback', views.view_feedback_view,name='view-feedback'),
    path('api/user-profile/<int:user_id>/', views.api_user_profile, name='api_user_profile'),
    path('user-profile/<int:user_id>/', views.user_profile_page, name='user_profile_page'),

    path('adminclick', views.adminclick_view),
    path('adminlogin', LoginView.as_view(template_name='ecom/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('view-customer', views.admin_view_users,name='view-customer'),

    # Added URL pattern for update-user to fix NoReverseMatch
    path('update-user/<int:pk>/', views.update_customer_view, name='update-user'),

    # Added URL pattern for bulk-update-users to fix NoReverseMatch
    path('bulk-update-users/', views.bulk_update_users, name='bulk-update-users'),

    # Added URL pattern for create-user to fix NoReverseMatch
    # Removed the create-user URL pattern as create_user_view does not exist
    path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),
    path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),

    # New URL for admin_view_users.html
    path('admin-view-users', views.admin_view_users, name='admin-view-users'),

    path('admin-products', views.admin_products_view,name='admin-products'),
    path('admin-add-product', views.admin_add_product_view,name='admin-add-product'),
    path('bulk-update-orders/', bulk_update_orders, name='bulk-update-orders'),
    path('delete-product/<int:pk>', views.delete_product_view,name='delete-product'),
    path('update-product/<int:pk>', views.update_product_view,name='update-product'),

    path('admin-view-booking', views.admin_view_booking_view, name='admin-view-booking'),
    path('admin-view-processing-orders', views.admin_view_processing_orders, name='admin-view-processing-orders'),
    path('admin-view-confirmed-orders', views.admin_view_confirmed_orders, name='admin-view-confirmed-orders'),
    path('admin-view-shipping-orders', views.admin_view_shipping_orders, name='admin-view-shipping-orders'),
    path('admin-view-delivered-orders', views.admin_view_delivered_orders, name='admin-view-delivered-orders'),
    path('admin-view-cancelled-orders', views.admin_view_cancelled_orders, name='admin-view-cancelled-orders'),
    path('delete-order/<int:pk>', views.delete_order_view,name='delete-order'),
    path('update-order/<int:pk>', views.update_order_view,name='update-order'),


    path('customersignup', views.customer_signup_view),
    path('customerlogin', LoginView.as_view(template_name='ecom/customerlogin.html'),name='customerlogin'),
    path('customer-home', views.customer_home_view,name='customer-home'),
    path('orders/pending/', views.pending_orders_view, name='pending-orders'),
    path('orders/to-ship/', views.to_ship_orders_view, name='to-ship-orders'),
    path('orders/to-receive/', views.to_receive_orders_view, name='to-receive-orders'),
    path('orders/delivered/', views.delivered_orders_view, name='delivered-orders'),
    path('orders/cancelled/', views.cancelled_orders_view, name='cancelled-orders'),
    path('my-order', views.my_order_view, name='my-order'),
    path('my-order/<int:pk>', views.my_order_view_pk, name='my-order-pk'),
    path('my-profile', views.my_profile_view,name='my-profile'),
    path('edit-profile', views.edit_profile_view,name='edit-profile'),
    path('download-invoice/<int:orderID>', views.download_invoice_view,name='download-invoice'),
    path('add-to-cart/<int:pk>', views.add_to_cart_view,name='add-to-cart'),
    path('cart', views.cart_view,name='cart'),
    path('remove-from-cart/<int:pk>', views.remove_from_cart_view,name='remove-from-cart'),
    path('customer-address', views.customer_address_view,name='customer-address'),
    path('payment-success/', views.payment_success_view,name='payment-success'),
    path('customizer/', views.jersey_customizer, name='customizer'),
    path('pre-order', views.pre_order, name='pre_order'),
    path('home', views.home,name='home'),
    # Removed the view_customer URL pattern as view_customer_view no longer exists
    # path('view_customer', views.view_customer_view, name='view_customer'),
    path('update-order/<int:pk>', views.update_order_view,name='update-order'),
    path('delete-order/<int:pk>', views.delete_order_view,name='delete-order'),
    path('facebook/', RedirectView.as_view(url='https://www.facebook.com/worksteamwear'), name='facebook'),
    path('instagram/', RedirectView.as_view(url='https://www.instagram.com/worksteamwear/'), name='instagram'),
    path('create/', views.create, name='create'),
    path('jersey-customizer/advanced/', views.jersey_customizer_advanced, name='jersey_customizer_advanced'),
    path('jersey-customizer/', views.jersey_customizer, name='jersey_customizer'),
    path('jersey-template/', views.jersey_template, name='jersey_template'),
    path('interactive-jersey/', views.interactive_jersey, name='interactive_jersey'),
    path('delete-inventory/<int:item_id>/', delete_inventory, name='delete_inventory'),
    path('edit-inventory/<int:item_id>/', edit_inventory, name='edit_inventory'), 
    path('place-order/', views.place_order, name='place_order'),
    path('cancel-order/<int:order_id>', views.cancel_order_view, name='cancel-order'),
    path('add-custom-jersey-to-cart/', views.add_custom_jersey_to_cart, name='add-custom-jersey-to-cart'),
    path('pay-with-gcash/', views.create_gcash_payment, name='pay_with_gcash'),
    path('payment-success/', views.payment_success_view, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
] + static(settings.MEDIA_URL, document_root=settings.STATIC_ROOT) if settings.DEBUG else []


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)