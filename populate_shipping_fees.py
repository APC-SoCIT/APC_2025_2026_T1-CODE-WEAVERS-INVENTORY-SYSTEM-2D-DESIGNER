import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ecom.models import ShippingFee

# Clear existing shipping fees
ShippingFee.objects.all().delete()
print('Cleared existing shipping fees')

# Define regions from Customer model
regions = [
    'NCR', 'CAR', 'Region I', 'Region II', 'Region III', 'Region IV-A', 
    'Region IV-B', 'Region V', 'Region VI', 'Region VII', 'Region VIII', 
    'Region IX', 'Region X', 'Region XI', 'Region XII', 'Region XIII', 
    'BARMM'
]

# Create shipping fees for different weight ranges and regions
shipping_data = []

# Standard courier rates (example rates)
for origin in regions:
    for destination in regions:
        # Same region shipping
        if origin == destination:
            shipping_data.extend([
                {'courier': 'Standard', 'origin': origin, 'destination': destination, 'weight': Decimal('1.00'), 'price': Decimal('50.00')},
                {'courier': 'Standard', 'origin': origin, 'destination': destination, 'weight': Decimal('2.00'), 'price': Decimal('70.00')},
                {'courier': 'Standard', 'origin': origin, 'destination': destination, 'weight': Decimal('5.00'), 'price': Decimal('120.00')},
            ])
        else:
            # Different region shipping (higher rates)
            shipping_data.extend([
                {'courier': 'Standard', 'origin': origin, 'destination': destination, 'weight': Decimal('1.00'), 'price': Decimal('80.00')},
                {'courier': 'Standard', 'origin': origin, 'destination': destination, 'weight': Decimal('2.00'), 'price': Decimal('120.00')},
                {'courier': 'Standard', 'origin': origin, 'destination': destination, 'weight': Decimal('5.00'), 'price': Decimal('200.00')},
            ])

# Create ShippingFee objects in batches
print(f'Creating {len(shipping_data)} shipping fee records...')
shipping_fees = []
for data in shipping_data:
    shipping_fees.append(ShippingFee(
        courier=data['courier'],
        origin_region=data['origin'],
        destination_region=data['destination'],
        weight_kg=data['weight'],
        price_php=data['price']
    ))

# Bulk create for efficiency
ShippingFee.objects.bulk_create(shipping_fees, batch_size=100)

print(f'Successfully created {ShippingFee.objects.count()} shipping fee records')

# Test the NCR to NCR shipping fee
ncr_fee = ShippingFee.objects.filter(origin_region='NCR', destination_region='NCR', weight_kg=Decimal('1.00')).first()
if ncr_fee:
    print(f'NCR to NCR (1kg): ₱{ncr_fee.price_php}')
else:
    print('NCR to NCR shipping fee not found')