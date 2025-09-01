from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ecom.models import Orders

class Command(BaseCommand):
    help = 'Automatically updates order statuses based on estimated delivery dates'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # Get all active orders (not delivered or cancelled)
        active_orders = Orders.objects.exclude(status__in=['Delivered', 'Cancelled'])
        
        for order in active_orders:
            # If no estimated delivery date, set it based on current status
            if not order.estimated_delivery_date:
                if order.status == 'Pending':
                    order.estimated_delivery_date = today + timedelta(days=7)
                elif order.status == 'Processing':
                    order.estimated_delivery_date = today + timedelta(days=5)
                elif order.status == 'Order Confirmed':
                    order.estimated_delivery_date = today + timedelta(days=3)
                elif order.status == 'Out for Delivery':
                    order.estimated_delivery_date = today + timedelta(days=1)
            
            # Update status based on time elapsed and estimated delivery date
            days_since_order = (today - order.order_date).days
            days_to_delivery = (order.estimated_delivery_date - today).days if order.estimated_delivery_date else 0
            
            new_status = order.status
            
            if days_since_order >= 1 and order.status == 'Pending':
                new_status = 'Processing'
            elif days_since_order >= 2 and order.status == 'Processing':
                new_status = 'Order Confirmed'
            elif days_to_delivery <= 1 and order.status == 'Order Confirmed':
                new_status = 'Out for Delivery'
            elif today >= order.estimated_delivery_date and order.status == 'Out for Delivery':
                new_status = 'Delivered'
            
            if new_status != order.status:
                order.status = new_status
                order.status_updated_at = timezone.now()
                order.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Updated order {order.id} status to {new_status}'
                ))