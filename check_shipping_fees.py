import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ecom.models import ShippingFee

print('ShippingFee records:', ShippingFee.objects.count())
print('\nAll ShippingFee records:')
for fee in ShippingFee.objects.all():
    print(f'{fee.courier}: {fee.origin_region} -> {fee.destination_region}, {fee.weight_kg}kg = ₱{fee.price_php}')

print('\nChecking for NCR to NCR shipping:')
ncr_to_ncr = ShippingFee.objects.filter(origin_region='NCR', destination_region='NCR')
print(f'NCR to NCR records: {ncr_to_ncr.count()}')
for fee in ncr_to_ncr:
    print(f'{fee.courier}: {fee.weight_kg}kg = ₱{fee.price_php}')