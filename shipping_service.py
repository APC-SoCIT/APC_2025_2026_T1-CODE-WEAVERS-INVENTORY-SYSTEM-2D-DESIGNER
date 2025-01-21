# shipping_service.py

class ShippingService:
    def __init__(self):
        self.tracking_info = {}

    def update_shipping_status(self, parcel_id, status):
        """Update the shipping status of a parcel."""
        self.tracking_info[parcel_id] = status
        print(f"Updated status for parcel {parcel_id}: {status}")

    def notify_customer(self, customer_id, parcel_id):
        """Notify the customer about the shipping status."""
        status = self.tracking_info.get(parcel_id, "Status not found")
        print(f"Notification to Customer {customer_id}: Your parcel {parcel_id} is currently '{status}'.")

    def notify_admin(self, parcel_id):
        """Notify the admin about successful delivery."""
        print(f"Admin Notification: Parcel {parcel_id} has been successfully delivered.")


# Example usage
if __name__ == "__main__":
    shipping_service = ShippingService()
    
    # Simulating the process
    parcel_id = "12345"
    customer_id = "C001"
    
    # Update shipping status
    shipping_service.update_shipping_status(parcel_id, "Out for delivery")
    
    # Notify customer
    shipping_service.notify_customer(customer_id, parcel_id)
    
    # Simulate successful delivery
    shipping_service.update_shipping_status(parcel_id, "Delivered")
    shipping_service.notify_admin(parcel_id)