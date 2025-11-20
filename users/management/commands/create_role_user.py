"""
Management command to create users with specific roles.

Usage:
python manage.py create_role_user --email admin@example.com --role admin --password admin123
python manage.py create_role_user --email manager@example.com --role manager --password manager123
python manage.py create_role_user --email developer@example.com --role developer --password dev123
python manage.py create_role_user --email client@example.com --role client --password client123
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a user with a specific role'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='User email address'
        )
        parser.add_argument(
            '--role',
            type=str,
            required=True,
            choices=['admin', 'manager', 'developer', 'client'],
            help='User role'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='User password'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='',
            help='User first name'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='',
            help='User last name'
        )
        parser.add_argument(
            '--is-staff',
            action='store_true',
            help='Make user staff'
        )
        parser.add_argument(
            '--is-superuser',
            action='store_true',
            help='Make user superuser'
        )

    def handle(self, *args, **options):
        email = options['email']
        role = options['role']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        is_staff = options['is_staff']
        is_superuser = options['is_superuser']

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise CommandError(f'User with email {email} already exists.')

        try:
            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=is_staff,
                is_superuser=is_superuser
            )

            # Update user profile with role
            if hasattr(user, 'profile'):
                user.profile.role = role
                user.profile.save()
            else:
                # Create profile if it doesn't exist
                UserProfile.objects.create(user=user, role=role)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created user {email} with role {role}'
                )
            )

            # Display user info
            self.stdout.write(f'User ID: {user.id}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Role: {user.profile.get_role_display()}')
            self.stdout.write(f'Is Staff: {user.is_staff}')
            self.stdout.write(f'Is Superuser: {user.is_superuser}')

        except Exception as e:
            raise CommandError(f'Error creating user: {str(e)}')

