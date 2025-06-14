from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from . import models
from .models import Product
from django.contrib.auth.forms import AuthenticationForm
from .models import InventoryItem


class CustomerUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model=models.Customer
        fields=['street_address', 'city', 'barangay', 'postal_code', 'mobile', 'profile_pic']

class ProductForm(forms.ModelForm):
    size = forms.ChoiceField(choices=[
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ], required=True)
    quantity = forms.IntegerField(min_value=0, required=False)

    class Meta:
        model=models.Product
        fields=['name','price','description','product_image']

    def __init__(self, *args, **kwargs):
        self.product_instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        size = cleaned_data.get('size')
        quantity = cleaned_data.get('quantity')

        if self.product_instance:
            # Check if size exists for this product
            from .models import ProductSize
            if size:
                exists = ProductSize.objects.filter(product=self.product_instance, size=size).exists()
                if not exists and (quantity is None or quantity == 0):
                    self.add_error('quantity', 'Quantity is required when adding a new size.')
        else:
            if quantity is None or quantity == 0:
                self.add_error('quantity', 'Quantity is required.')

        return cleaned_data

#address of shipment
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=models.Feedback
        fields=['name','feedback']

#for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model=models.Orders
        fields=['status', 'estimated_delivery_date', 'notes']
        widgets = {
            'estimated_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3})
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk:  # If this is an existing instance
            original = models.Orders.objects.get(pk=self.instance.pk)
            if instance.status != original.status:
                instance.status_updated_at = timezone.now()
        else:  # If this is a new instance
            instance.status_updated_at = timezone.now()
        if commit:
            instance.save()
        return instance

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))

class InventoryForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'quantity', 'description']

class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
