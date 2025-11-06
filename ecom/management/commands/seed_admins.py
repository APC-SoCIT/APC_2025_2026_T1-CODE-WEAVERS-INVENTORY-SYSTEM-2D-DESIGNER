from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from ecom import models as ecom_models


class Command(BaseCommand):
    help = "Seed admin roles (Groups) and create SuperAdmin + Manager accounts with scoped permissions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-groups",
            action="store_true",
            help="Recreate role groups and re-apply permissions",
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write(self.style.NOTICE("Setting up admin roles and users..."))

            # 1) Create or reset Groups
            groups = {
                "SuperAdmins": None,
                "Managers": None,
                "Staff": None,
            }

            for name in groups.keys():
                group, _created = Group.objects.get_or_create(name=name)
                if options.get("reset_groups"):
                    group.permissions.clear()
                groups[name] = group

            # Utility to fetch model permissions by codename prefix
            def perms_for_model(model, actions=("view", "add", "change", "delete")):
                ct = ContentType.objects.get_for_model(model)
                codenames = [f"{action}_{model._meta.model_name}" for action in actions]
                return list(Permission.objects.filter(content_type=ct, codename__in=codenames))

            # Map permissions for Managers (scoped access)
            manager_perms = []
            # User management (create accounts for employees, update access)
            manager_perms += perms_for_model(User, actions=("view", "add", "change"))
            # Allow managers to assign groups to users (no add/delete group)
            manager_perms += perms_for_model(Group, actions=("view", "change"))
            # Orders & reporting
            manager_perms += perms_for_model(ecom_models.Orders, actions=("view", "change"))
            manager_perms += perms_for_model(ecom_models.OrderItem, actions=("view",))
            manager_perms += perms_for_model(ecom_models.BulkOrderOperation, actions=("view", "add"))
            manager_perms += perms_for_model(ecom_models.DeliveryStatusLog, actions=("view",))
            # Inventory & products (overlooking billing/inventory reporting)
            manager_perms += perms_for_model(ecom_models.InventoryItem, actions=("view", "change"))
            manager_perms += perms_for_model(ecom_models.Product, actions=("view",))
            # Customers (read-only)
            manager_perms += perms_for_model(ecom_models.Customer, actions=("view",))

            groups["Managers"].permissions.set(manager_perms)

            # Map permissions for Staff (day-to-day ops: orders, stocks, sales, customer accounts)
            staff_perms = []
            staff_perms += perms_for_model(ecom_models.Orders, actions=("view", "change"))
            staff_perms += perms_for_model(ecom_models.OrderItem, actions=("view"))
            staff_perms += perms_for_model(ecom_models.InventoryItem, actions=("view", "change"))
            staff_perms += perms_for_model(ecom_models.Product, actions=("view"))
            staff_perms += perms_for_model(ecom_models.Customer, actions=("view", "change"))
            staff_perms += perms_for_model(ecom_models.Feedback, actions=("view", "add"))

            groups["Staff"].permissions.set(staff_perms)

            # 2) Ensure SuperAdmins group exists (optional: assign broad view permissions)
            # SuperAdmins users will be is_superuser=True which gives root access.

            # 3) Create users and assign groups
            def upsert_user(username: str, password: str, is_staff: bool, is_superuser: bool, group: Group | None):
                user, created = User.objects.get_or_create(username=username)
                user.is_staff = is_staff
                user.is_superuser = is_superuser
                user.set_password(password)
                user.save()
                if group:
                    user.groups.set([group])
                else:
                    user.groups.clear()
                return user, created

            # SuperAdmin account
            super_user, created_super = upsert_user(
                username="worksteamwear",
                password="worksteamwearadmin",
                is_staff=True,
                is_superuser=True,
                group=groups["SuperAdmins"],
            )

            # Corresponding SuperAdmin record (for admin dashboard metadata)
            ecom_models.SuperAdmin.objects.update_or_create(
                user=super_user,
                defaults={
                    "employee_id": "ROOT-0001",
                    "department": "Administration",
                    "position": "SuperAdmin",
                    "is_active": True,
                },
            )

            # Managers
            manager_specs = [
                ("johndavid0103", "manager0103"),
                ("elijah567", "elijahmanager"),
                ("marvinsum", "marvinmanager"),
            ]

            for username, password in manager_specs:
                upsert_user(
                    username=username,
                    password=password,
                    is_staff=True,
                    is_superuser=False,
                    group=groups["Managers"],
                )

            self.stdout.write(self.style.SUCCESS("Admin roles and users have been seeded successfully."))
