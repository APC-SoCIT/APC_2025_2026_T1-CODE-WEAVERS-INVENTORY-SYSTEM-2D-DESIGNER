from django.core.management.base import BaseCommand
from django.db import transaction

from ecom.models import Orders, OrderItem, CustomOrderItem


class Command(BaseCommand):
    help = (
        "Clear all pre-order custom items (CustomOrderItem with is_pre_order=True). "
        "Optionally remove orphan Orders that no longer have any items."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show counts that would be deleted without performing deletion",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Proceed without interactive confirmation",
        )
        parser.add_argument(
            "--keep-orders",
            action="store_true",
            help="Keep Orders even if they become orphaned after clearing pre-orders",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        proceed = options.get("yes", False)
        keep_orders = options.get("keep_orders", False)

        pre_qs = CustomOrderItem.objects.filter(is_pre_order=True)
        pre_order_item_count = pre_qs.count()
        affected_order_ids = list(
            pre_qs.values_list("order_id", flat=True).distinct()
        )

        # Determine orders that would become orphaned (no OrderItem and no non-pre CustomOrderItem)
        orphan_order_ids = []
        for oid in affected_order_ids:
            has_orderitem = OrderItem.objects.filter(order_id=oid).exists()
            has_non_pre_custom = CustomOrderItem.objects.filter(
                order_id=oid, is_pre_order=False
            ).exists()
            if not has_orderitem and not has_non_pre_custom:
                orphan_order_ids.append(oid)

        counts = {
            "pre_order_items": pre_order_item_count,
            "affected_orders": len(affected_order_ids),
            "orphan_orders": len(orphan_order_ids),
        }

        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY RUN] Would delete: {counts}"))
            return

        if not proceed:
            self.stdout.write(
                self.style.ERROR(
                    "Refusing to delete without --yes. Re-run with --dry-run to preview or --yes to execute."
                )
            )
            return

        with transaction.atomic():
            # Delete pre-order custom items
            deleted_items, _ = pre_qs.delete()

            # Optionally delete orphan orders
            deleted_orders = 0
            if not keep_orders and orphan_order_ids:
                deleted_orders = Orders.objects.filter(id__in=orphan_order_ids).delete()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted pre-order items: {deleted_items}; Deleted orphan orders: {deleted_orders}"
            )
        )

