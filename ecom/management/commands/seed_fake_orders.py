from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

import random
import string
from datetime import datetime, timedelta, date
from decimal import Decimal

from ecom.models import Customer, Product, Orders, OrderItem


def random_order_ref():
    # 12-char reference: OR + 10 random uppercase letters/digits
    return "OR" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


class Command(BaseCommand):
    help = "Seed fake orders and items within a date range to test analytics"

    def add_arguments(self, parser):
        parser.add_argument("--start", type=str, required=True, help="Start date (YYYY-MM-DD)")
        parser.add_argument("--end", type=str, required=True, help="End date (YYYY-MM-DD)")
        parser.add_argument("--per-day", type=int, default=3, help="Number of orders to create per day")
        parser.add_argument("--include-cancelled", action="store_true", help="Include some cancelled orders")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing to DB")

    def handle(self, *args, **options):
        start_str = options["--start"] if "--start" in options else options["start"]
        end_str = options["--end"] if "--end" in options else options["end"]
        per_day = options["per_day"]
        include_cancelled = options["include_cancelled"]
        dry_run = options["dry_run"]

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            return self.stderr.write(self.style.ERROR("Invalid date format. Use YYYY-MM-DD."))

        if start_date > end_date:
            return self.stderr.write(self.style.ERROR("Start date must be before or equal to end date."))

        # Ensure we have Customers and Products
        customers = list(Customer.objects.select_related("user").all())
        products = list(Product.objects.all())

        created_customers = 0
        created_products = 0

        if not customers:
            # Create 3 demo users/customers
            for i in range(3):
                username = f"demo_user_{i+1}"
                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": f"{username}@example.com",
                        "first_name": f"Demo{i+1}",
                        "last_name": "User",
                    },
                )
                if not hasattr(user, "customer"):
                    customer = Customer.objects.create(
                        user=user,
                        region="NCR",
                        province="Metro Manila",
                        citymun="Quezon City",
                        barangay="Bagumbayan",
                        street_address=f"{100+i} Ecom Ave",
                        postal_code=1100,
                        mobile="956 000 0000",
                    )
                    customers.append(customer)
                    created_customers += 1

        if not products:
            # Create 5 demo products
            for i in range(5):
                product = Product.objects.create(
                    name=f"Jersey {i+1}",
                    price=Decimal(random.choice([499, 599, 699, 799, 899])),
                    description="Demo jersey product",
                    quantity=100,
                )
                products.append(product)
                created_products += 1

        self.stdout.write(self.style.NOTICE(
            f"Using {len(customers)} customers ({created_customers} created) and {len(products)} products ({created_products} created)."
        ))

        # Status and payment method distributions
        status_pool = [
            ("Delivered", 0.30),
            ("Out for Delivery", 0.10),
            ("Order Confirmed", 0.15),
            ("Processing", 0.20),
            ("Pending", 0.20),
        ]
        if include_cancelled:
            status_pool.append(("Cancelled", 0.05))

        payment_pool = [
            ("cod", 0.50),
            ("paypal", 0.25),
            ("gcash", 0.25),
        ]

        def pick_weighted(pool):
            r = random.random()
            acc = 0
            for val, w in pool:
                acc += w
                if r <= acc:
                    return val
            return pool[-1][0]

        total_orders = 0
        total_items = 0
        total_revenue = Decimal("0.00")

        @transaction.atomic
        def create_for_day(day: date):
            nonlocal total_orders, total_items, total_revenue

            for _ in range(per_day):
                customer = random.choice(customers)
                status = pick_weighted(status_pool)
                payment = pick_weighted(payment_pool)

                created_dt = datetime.combine(day, datetime.min.time()) + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
                est_delivery = None
                if status in ["Processing", "Order Confirmed", "Out for Delivery", "Delivered"]:
                    est_delivery = day + timedelta(days=random.randint(2, 5))

                order = Orders(
                    customer=customer,
                    email=customer.user.email or f"{customer.user.username}@example.com",
                    address=customer.get_full_address,
                    mobile=customer.mobile or "956 111 1111",
                    status=status,
                    payment_method=payment,
                    order_ref=random_order_ref(),
                    delivery_fee=Decimal(random.choice([0, 59, 79, 99])),
                    estimated_delivery_date=est_delivery,
                )
                if payment in ["paypal", "gcash"] and status != "Pending":
                    order.transaction_id = "TXN" + "".join(random.choices(string.digits, k=10))

                if dry_run:
                    # Skip DB write, just simulate
                    items_count = random.randint(1, 3)
                    items_total = Decimal("0.00")
                    for _j in range(items_count):
                        product = random.choice(products)
                        # Price in Product is PositiveIntegerField, cast to Decimal
                        price = Decimal(product.price)
                        qty = random.randint(1, 3)
                        items_total += price * qty
                    total = items_total + Decimal(order.delivery_fee)
                    total_orders += 1
                    total_items += items_count
                    total_revenue += total
                    continue

                # Persist order
                order.save()

                # Attach items
                items_count = random.randint(1, 3)
                items_total = Decimal("0.00")
                for _j in range(items_count):
                    product = random.choice(products)
                    price = Decimal(product.price)
                    qty = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price=price,
                    )
                    items_total += price * qty

                # Update timestamps and order_date to the target day
                Orders.objects.filter(id=order.id).update(
                    created_at=created_dt,
                    updated_at=created_dt,
                    order_date=day,
                    status_updated_at=created_dt,
                )

                total = items_total + Decimal(order.delivery_fee)
                total_orders += 1
                total_items += items_count
                total_revenue += total

        # Iterate through the date range
        day = start_date
        created_days = 0
        while day <= end_date:
            if dry_run:
                # Simulate creation without DB writes
                for _ in range(per_day):
                    # Simulate revenue computation
                    customer = random.choice(customers)
                    _ = customer  # no-op to quiet lints
                created_days += 1
            else:
                create_for_day(day)
                created_days += 1
            day += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete for {created_days} day(s): orders={total_orders}, items={total_items}, revenue=₱{total_revenue:.2f}"
        ))
