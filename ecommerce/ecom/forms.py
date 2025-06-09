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

class CustomerSignupForm(CustomerForm):
    privacy_policy = forms.BooleanField(
        required=True,
        label='I agree to the Privacy Policy',
        error_messages={'required': 'You must accept the privacy policy to create an account'}
    )
    
    class Meta:
        model=models.Customer
        fields=['street_address', 'city', 'barangay', 'postal_code', 'mobile', 'profile_pic']

class ProductForm(forms.ModelForm):
    class Meta:
        model=models.Product
        fields=['name','price','description','product_image','quantity','size']

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
