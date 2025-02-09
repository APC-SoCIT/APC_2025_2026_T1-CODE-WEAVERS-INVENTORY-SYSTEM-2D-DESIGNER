from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Order

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['design_image']
