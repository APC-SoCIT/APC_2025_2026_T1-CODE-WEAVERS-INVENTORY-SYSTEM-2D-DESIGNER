import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ecom.models import Orders, ShippingFee

# Create region mapping from customer format to shipping fee format
region_mapping = {
    'Region R1': 'Region I',
    'Region R2': 'Region II', 
    'Region R3': 'Region III',
    'Region R4A': 'Region IV-A',
    'Region R4B': 'Region IV-B',
    'Region R5': 'Region V',
    'Region R6': 'Region VI',
    'Region R7': 'Region VII',
    'Region R8': 'Region VIII',
    'Region R9': 'Region IX',
    'Region R10': 'Region X',
    'Region R11': 'Region XI',
    'Region R12': 'Region XII',
    'Region R13': 'Region XIII',
    'NCR': 'NCR',
    'CAR': 'CAR',
    'BARMM': 'BARMM'
}

def get_mapped_region(customer_region):
    """Map customer region format to shipping fee format"""
    return region_mapping.get(customer_region, 'NCR')  # Default to NCR if not found

def get_shipping_fee_fixed(origin_region, destination_region, weight_kg):
    """Get shipping fee with proper region mapping"""
    try:
        # Map regions to proper format
        mapped_origin = get_mapped_region(origin_region)
        mapped_destination = get_mapped_region(destination_region)
        
        # Find the shipping fee
        shipping_fee = ShippingFee.objects.filter(
            origin_region=mapped_origin,
            destination_region=mapped_destination,
            weight_kg__gte=weight_kg
        ).order_by('weight_kg').first()
        
        if shipping_fee:
            return shipping_fee.price_php
        else:
            print(f'No shipping fee found for {mapped_origin} -> {mapped_destination}, weight {weight_kg}kg')
            return Decimal('50.00')  # Default fee
    except Exception as e:
        print(f'Error getting shipping fee: {e}')
        return Decimal('50.00')  # Default fee

# Get all orders with delivery_fee = 0
orders_to_update = Orders.objects.filter(delivery_fee=0)
print(f'Found {orders_to_update.count()} orders with delivery_fee = 0')

updated_count = 0
for order in orders_to_update:
    try:
        # Get customer region
        customer_region = order.customer.region if order.customer.region else 'NCR'
        
        # Calculate delivery fee using the fixed mapping
        delivery_fee = get_shipping_fee_fixed('NCR', customer_region, Decimal('1.0'))
        
        # Update the order
        order.delivery_fee = delivery_fee
        order.save()
        
        mapped_region = get_mapped_region(customer_region)
        print(f'Updated Order {order.order_ref}: {customer_region} ({mapped_region}) -> ₱{delivery_fee}')
        updated_count += 1
        
    except Exception as e:
        print(f'Error updating order {order.order_ref}: {e}')

print(f'\nSuccessfully updated {updated_count} orders')

# Verify the updates
print('\nVerification - First 5 orders:')
for order in Orders.objects.all()[:5]:
    print(f'Order {order.order_ref}: Customer region = {order.customer.region}, Delivery fee = ₱{order.delivery_fee}')