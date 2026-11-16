from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            User.objects.create_superuser("admin","123")
            self.stdout.write(self.style.SUCCESS("Successfully created admin user"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Error creating admin user"))
