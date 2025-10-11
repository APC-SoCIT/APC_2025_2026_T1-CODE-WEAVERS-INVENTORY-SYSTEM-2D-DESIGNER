from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a superuser account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Username for the admin account')
        parser.add_argument('--email', type=str, default='admin@worksteamwear.com', help='Email for the admin account')
        parser.add_argument('--password', type=str, default='admin123', help='Password for the admin account')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists!')
            )
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Admin user "{username}" created successfully!')
        )
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
