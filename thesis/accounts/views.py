from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileForm
from .models import UserProfile

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                return render(request, 'accounts/register.html', {'error': 'Username already exists'})
            else:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('home')
        else:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})
    else:
        return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            return redirect('loginfailed')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'user_profile': user_profile})

@login_required
def admin_dashboard(request):
    return render(request, 'accounts/admin-dashboard.html')

def home(request):
    return render(request, 'accounts/home.html')

def create(request):
    return render(request, 'accounts/create.html')

