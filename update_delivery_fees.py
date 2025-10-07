import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ecom.models import Orders, ShippingFee
from ecom.views import get_shipping_fee

# Get all orders with delivery_fee = 0
orders_to_update = Orders.objects.filter(delivery_fee=0)
print(f'Found {orders_to_update.count()} orders with delivery_fee = 0')

updated_count = 0
for order in orders_to_update:
    try:
        # Get customer region
        customer_region = order.customer.region if order.customer.region else 'NCR'
        
        # Calculate delivery fee using the same logic as payment_success_view
        delivery_fee = get_shipping_fee('NCR', customer_region, Decimal('1.0'))
        
        # Update the order
        order.delivery_fee = delivery_fee
        order.save()
        
        print(f'Updated Order {order.order_ref}: {customer_region} -> ₱{delivery_fee}')
        updated_count += 1
        
    except Exception as e:
        print(f'Error updating order {order.order_ref}: {e}')

print(f'\nSuccessfully updated {updated_count} orders')

# Verify the updates
print('\nVerification - First 5 orders:')
for order in Orders.objects.all()[:5]:
    print(f'Order {order.order_ref}: Customer region = {order.customer.region}, Delivery fee = ₱{order.delivery_fee}')