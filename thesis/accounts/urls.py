from django.urls import path
from .views import register, login_view, logout_view, profile, admin_dashboard
from django.shortcuts import render
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('create/', views.create, name='create'),
    path('register/', views.register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('loginfailed/', lambda request: render(request, 'accounts/login_failed.html'), name='loginfailed'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]
