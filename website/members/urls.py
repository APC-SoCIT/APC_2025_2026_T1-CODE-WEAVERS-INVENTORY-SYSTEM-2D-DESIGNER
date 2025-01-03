# website/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('index/', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('resume/', views.resume, name='resume'),
    path('projects/', views.projects, name='projects'),
    path('about/', views.about, name='about'),
    path('signin/', views.signin, name='signin'),
    path('store/', views.store, name='store'),
    path('profile/', views.profile, name='profile'),
    path('myfirst/', views.myfirst, name='myfirst'),
    path('admin/', views.admin, name='admin'),
    path('adminlogin/', views.adminlogin, name='adminlogin'),
]
