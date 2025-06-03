from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    COUNTRY_CHOICES = [
        ('PH', 'Philippines'),
        ('US', 'United States')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/CustomerProfilePic/', null=True, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='PH')
    city = models.CharField(max_length=50)
    barangay = models.CharField(max_length=50)
    street_address = models.CharField(max_length=100)
    postal_code = models.PositiveIntegerField()
    mobile = models.PositiveIntegerField()

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    @property
    def get_full_address(self):
        return f"{self.street_address}, {self.barangay}, {self.city}, {self.postal_code}"

    def __str__(self):
        return self.user.first_name


class InventoryItem(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=40)
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True)
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=40)
    quantity = models.PositiveIntegerField(default=0)
    SIZE_CHOICES = (
        ('S', 'Small'),
        ('XS', 'Extra Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    )
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, default='M')
    
    def __str__(self):
        return self.name

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=5, choices=Product.SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)



class Orders(models.Model):
    STATUS = (
        ('Pending', 'Pending - Awaiting Payment'),
        ('Processing', 'Processing - Payment Confirmed'),
        ('Order Confirmed', 'Order Confirmed - In Production'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    )
    PAYMENT_METHODS = (
        ('cod', 'Cash on Delivery'),
        ('paypal', 'PayPal')
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='When the order was created')
    updated_at = models.DateTimeField(auto_now=True, help_text='When the order was last updated')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    email = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    mobile = models.CharField(max_length=20, null=True)
    order_date = models.DateField(auto_now_add=True, null=True, help_text='Date when order was placed')
    status = models.CharField(max_length=50, null=True, choices=STATUS, default='Pending', help_text='Current status of the order')
    status_updated_at = models.DateTimeField(null=True, blank=True, help_text='When the status was last changed')
    size = models.CharField(max_length=20)
    quantity = models.IntegerField(default=1)
    estimated_delivery_date = models.DateField(null=True, blank=True, help_text='Estimated delivery date')
    notes = models.TextField(blank=True, null=True, help_text='Additional notes about the order')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cod', help_text='Payment method for the order')
    order_ref = models.CharField(max_length=12, unique=True, null=True, blank=True, help_text='Unique short order reference ID')

class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=5, choices=Product.SIZE_CHOICES, null=True, blank=True)


class Feedback(models.Model):
    name=models.CharField(max_length=40)
    feedback=models.CharField(max_length=500)
    date= models.DateField(auto_now_add=True,null=True)
    def __str__(self):
        return self.name


