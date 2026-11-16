from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Creates an admin superuser with role='admin' and customizable CLI arguments."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: "admin")'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='123',
            help='Admin password (default: "123")'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default=None,
            help='Admin phone number (e.g. +998901234567)'
        )
        parser.add_argument(
            '--first-name',
            dest='first_name',
            type=str,
            default='Admin',
            help='Admin first name'
        )
        parser.add_argument(
            '--last-name',
            dest='last_name',
            type=str,
            default='User',
            help='Admin last name'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        phone = options.get('phone')
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')

        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                    'is_staff': True,
                    'is_superuser': True,
                    'role': 'admin',
                }
            )

            if created:
                user.set_password(password)
                user.role = 'admin'
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created admin user: '{username}' with role='admin'"
                    )
                )
            else:
                user.role = 'admin'
                user.is_staff = True
                user.is_superuser = True
                user.set_password(password)
                if phone:
                    user.phone = phone
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                user.save()
                self.stdout.write(
                    self.style.WARNING(
                        f"Admin user '{username}' already existed. Updated password, role='admin' and permissions."
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating admin user: {str(e)}"))
            raise CommandError(f"Failed to create admin user: {str(e)}")
