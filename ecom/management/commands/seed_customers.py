from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from ecom.models import Customer


REAL_CUSTOMERS = [
    {"first_name": "Juan", "last_name": "Dela Cruz", "region": "NCR", "province": "Metro Manila", "city": "Quezon City", "barangay": "Bagumbayan", "street": "12 Sampaguita St", "postal": 1100, "mobile": "912 345 6789"},
    {"first_name": "Maria", "last_name": "Santos", "region": "NCR", "province": "Metro Manila", "city": "Makati", "barangay": "Poblacion", "street": "45 Kalayaan Ave", "postal": 1209, "mobile": "915 234 5678"},
    {"first_name": "Jose", "last_name": "Ramirez", "region": "R4A", "province": "Cavite", "city": "Dasmariñas", "barangay": "Salawag", "street": "78 Mabini St", "postal": 4114, "mobile": "918 765 4321"},
    {"first_name": "Anna", "last_name": "Reyes", "region": "R4A", "province": "Laguna", "city": "Calamba", "barangay": "Real", "street": "33 Rizal Blvd", "postal": 4027, "mobile": "917 222 3344"},
    {"first_name": "Paolo", "last_name": "Garcia", "region": "R3", "province": "Bulacan", "city": "San Jose del Monte", "barangay": "Sto. Cristo", "street": "99 Maginhawa St", "postal": 3023, "mobile": "919 111 2233"},
    {"first_name": "Liza", "last_name": "Villanueva", "region": "R4A", "province": "Rizal", "city": "Antipolo", "barangay": "Cupang", "street": "18 Sumulong Hwy", "postal": 1870, "mobile": "916 555 6677"},
    {"first_name": "Mark", "last_name": "Cruz", "region": "R4A", "province": "Batangas", "city": "Lipa", "barangay": "Sabang", "street": "7 Laurel St", "postal": 4217, "mobile": "913 777 8899"},
    {"first_name": "Katrina", "last_name": "Flores", "region": "R3", "province": "Pampanga", "city": "Angeles", "barangay": "Malabanias", "street": "101 Clark Ave", "postal": 2009, "mobile": "912 808 7070"},
    {"first_name": "Ramon", "last_name": "Aquino", "region": "R1", "province": "Ilocos Norte", "city": "Laoag", "barangay": "Barangay 2", "street": "56 Burgos St", "postal": 2900, "mobile": "914 333 2211"},
    {"first_name": "Angela", "last_name": "Soriano", "region": "R2", "province": "Cagayan", "city": "Tuguegarao", "barangay": "Pengue-Ruyu", "street": "22 Bonifacio St", "postal": 3500, "mobile": "917 909 8080"},
    {"first_name": "Cesar", "last_name": "Mendoza", "region": "R7", "province": "Cebu", "city": "Cebu City", "barangay": "Mabolo", "street": "88 Hernan Cortes", "postal": 6000, "mobile": "915 606 5050"},
    {"first_name": "Nina", "last_name": "Del Rosario", "region": "R11", "province": "Davao del Sur", "city": "Davao City", "barangay": "Matina", "street": "64 Tulip Dr", "postal": 8000, "mobile": "918 202 1010"},
    {"first_name": "Patrick", "last_name": "Lopez", "region": "R6", "province": "Iloilo", "city": "Iloilo City", "barangay": "Jaro", "street": "3 E. Lopez St", "postal": 5000, "mobile": "913 909 6060"},
    {"first_name": "Bea", "last_name": "Ramos", "region": "R5", "province": "Albay", "city": "Legazpi", "barangay": "Bagong Bayan", "street": "14 Embarcadero", "postal": 4500, "mobile": "916 444 5555"},
    {"first_name": "Erwin", "last_name": "Osorio", "region": "R10", "province": "Misamis Oriental", "city": "Cagayan de Oro", "barangay": "Kauswagan", "street": "70 J.R. Borja Ext", "postal": 9000, "mobile": "919 303 4040"},
    {"first_name": "Jessa", "last_name": "Pineda", "region": "R9", "province": "Zamboanga del Sur", "city": "Zamboanga City", "barangay": "Tetuan", "street": "25 Veterans Ave", "postal": 7000, "mobile": "917 121 2121"},
    {"first_name": "Noel", "last_name": "Santiago", "region": "R12", "province": "South Cotabato", "city": "General Santos", "barangay": "Bula", "street": "11 Tiongson St", "postal": 9500, "mobile": "912 919 8282"},
    {"first_name": "Carla", "last_name": "Gonzales", "region": "R13", "province": "Agusan del Norte", "city": "Butuan", "barangay": "Bancasi", "street": "8 Montilla Blvd", "postal": 8600, "mobile": "914 515 6161"},
    {"first_name": "Miguel", "last_name": "Fernandez", "region": "NCR", "province": "Metro Manila", "city": "Taguig", "barangay": "Ususan", "street": "77 C5 Rd", "postal": 1630, "mobile": "915 818 9191"},
    {"first_name": "Sofia", "last_name": "Navarro", "region": "NCR", "province": "Metro Manila", "city": "Pasig", "barangay": "Santolan", "street": "19 Amang Rodriguez", "postal": 1609, "mobile": "918 737 4747"},
]


def unique_username(base: str) -> str:
    base = base.lower().replace(" ", "_")
    candidate = base
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}{suffix}"
        suffix += 1
    return candidate


class Command(BaseCommand):
    help = "Seed at least N realistic customer accounts (default 15). Idempotent creation."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=15, help="Number of customers to create (min 15)")
        parser.add_argument("--password", type=str, default="Customer123!", help="Default password for created users")

    @transaction.atomic
    def handle(self, *args, **options):
        count = max(15, options.get("count", 15))
        password = options.get("password")

        created = []
        checked = 0

        for entry in REAL_CUSTOMERS:
            if len(created) >= count:
                break

            full_base = f"{entry['first_name']}_{entry['last_name']}"
            username = unique_username(full_base)

            # Use a consistent email schema
            email = f"{entry['first_name'].lower()}.{entry['last_name'].lower()}@example.com"

            # Avoid duplicating by email and name combination
            existing = User.objects.filter(email=email, first_name=entry["first_name"], last_name=entry["last_name"]).first()
            if existing and hasattr(existing, "customer"):
                checked += 1
                continue

            user = existing or User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=entry["first_name"],
                last_name=entry["last_name"],
            )
            user.is_staff = False
            user.is_superuser = False
            user.save()

            if not hasattr(user, "customer"):
                Customer.objects.create(
                    user=user,
                    region=entry["region"],
                    province=entry["province"],
                    citymun=entry["city"],
                    barangay=entry["barangay"],
                    street_address=entry["street"],
                    postal_code=entry["postal"],
                    mobile=entry["mobile"],
                )

            created.append({
                "username": user.username,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
            })

        self.stdout.write(self.style.SUCCESS(f"Created {len(created)} customer accounts (checked {checked})."))
        for c in created:
            self.stdout.write(f"- {c['username']} | {c['name']} | {c['email']}")

