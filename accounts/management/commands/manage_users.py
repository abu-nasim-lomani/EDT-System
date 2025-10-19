# accounts/management/commands/manage_users.py

from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Manage users easily - create, delete, list users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['list', 'create', 'delete', 'clear_all'],
            help='Action to perform',
            required=True
        )
        parser.add_argument('--username', type=str, help='Username')
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--password', type=str, help='Password')
        parser.add_argument('--role', type=str, choices=['MANAGEMENT', 'MANAGER'], help='User role')
        parser.add_argument('--superuser', action='store_true', help='Make user a superuser')

    def handle(self, *args, **options):
        action = options['action']

        if action == 'list':
            self.list_users()
        elif action == 'create':
            self.create_user(options)
        elif action == 'delete':
            self.delete_user(options['username'])
        elif action == 'clear_all':
            self.clear_all_users()

    def list_users(self):
        users = User.objects.all()
        if not users:
            self.stdout.write(self.style.WARNING('No users found.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {users.count()} users:'))
        for user in users:
            status = []
            if user.is_superuser:
                status.append('SUPERUSER')
            if user.is_staff:
                status.append('STAFF')
            status_str = f" ({', '.join(status)})" if status else ""
            
            self.stdout.write(f'  - {user.username} | {user.email} | Role: {user.role}{status_str}')

    def create_user(self, options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        role = options.get('role', 'MANAGER')
        is_superuser = options.get('superuser', False)

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR('Username, email, and password are required.'))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User with username "{username}" already exists.'))
            return

        try:
            if is_superuser:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                user.role = role
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role
                )
                self.stdout.write(self.style.SUCCESS(f'User "{username}" created successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user: {e}'))

    def delete_user(self, username):
        if not username:
            self.stdout.write(self.style.ERROR('Username is required for deletion.'))
            return

        try:
            user = User.objects.get(username=username)
            user.delete()
            self.stdout.write(self.style.SUCCESS(f'User "{username}" deleted successfully.'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found.'))

    def clear_all_users(self):
        count = User.objects.count()
        if count == 0:
            self.stdout.write(self.style.WARNING('No users to delete.'))
            return

        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'All {count} users deleted successfully.'))