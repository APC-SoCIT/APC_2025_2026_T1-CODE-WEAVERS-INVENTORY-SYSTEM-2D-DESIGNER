from django import forms
from .models import Product
from .models import Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'quantity', 'price']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'customer_name', 'quantity', 'status']

