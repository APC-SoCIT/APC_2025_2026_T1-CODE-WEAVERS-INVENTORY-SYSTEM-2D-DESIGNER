from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from . import models
from .models import Product, InventoryItem


# User registration form
class CustomerUserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


# Customer personal details form
class CustomerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use model REGION_CHOICES for region field (code as value, label as display)
        self.fields['region'].choices = models.Customer.REGION_CHOICES
        self.fields['region'].widget = forms.Select()
        self.fields['region'].required = True
        # Fix: If POSTed value is a label, convert to code
        region_value = self.data.get('region') or self.initial.get('region')
        if region_value:
            # If the value is a label, convert to code
            code = None
            for c, label in models.Customer.REGION_CHOICES:
                if region_value == label or region_value == c:
                    code = c
                    break
            if code:
                self.data = self.data.copy()
                self.data['region'] = code
                self.fields['region'].initial = code
        # Allow any value for city and barangay by setting choices to the POSTed or initial value if present
        for field in ['city', 'barangay']:
            value = self.data.get(field, None) or self.initial.get(field, None)
            if value:
                self.fields[field].choices = [(value, value)]
            else:
                self.fields[field].choices = []
            self.fields[field].widget = forms.Select()
            self.fields[field].required = True

    class Meta:
        model = models.Customer
        fields = ['street_address', 'city', 'barangay', 'postal_code', 'mobile', 'profile_pic', 'region']
        widgets = {
            'city': forms.Select(choices=[]),
            'barangay': forms.Select(choices=[]),
        }


# Extended signup form with privacy agreement
class CustomerSignupForm(CustomerForm):
    privacy_policy = forms.BooleanField(
        required=True,
        label='I agree to the Privacy Policy',
        error_messages={'required': 'You must accept the privacy policy to create an account'}
    )

    class Meta(CustomerForm.Meta):
        fields = CustomerForm.Meta.fields + ['region']


# Product creation and update form
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
        model = models.Product
        fields = ['name', 'price', 'description', 'product_image', 'quantity', 'size']


# Address form during checkout or delivery
class AddressForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput())
    mobile = forms.CharField(max_length=15, widget=forms.TextInput())
    address = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3}))


# Feedback form from customers
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = models.Feedback
        fields = ['name', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 3})
        }


# For updating order status and delivery details
class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Orders
        fields = ['status', 'estimated_delivery_date', 'notes']
        widgets = {
            'estimated_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk:  # Updating an existing order
            original = models.Orders.objects.get(pk=self.instance.pk)
            if instance.status != original.status:
                instance.status_updated_at = timezone.now()
        else:  # New order
            instance.status_updated_at = timezone.now()
        if commit:
            instance.save()
        return instance


# Contact us page form
class ContactusForm(forms.Form):
    name = forms.CharField(max_length=30, widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput())
    message = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 30})
    )


# Inventory management form for staff
class InventoryForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'quantity', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


# Login form for customers
class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=100, widget=forms.TextInput())
    password = forms.CharField(label='Password', widget=forms.PasswordInput())