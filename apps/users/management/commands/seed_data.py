from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import UserRole

User = get_user_model()


class Command(BaseCommand):
    help = "Barcha modellar uchun sifatli va realistik mock ma'lumotlarni bazaga to'ldiradi."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Mock ma'lumotlarni yaratish boshlandi..."))

        # 1. Admin yaratish
        admins_data = [
            {
                "username": "admin",
                "password": "123",
                "first_name": "Asosiy",
                "last_name": "Administrator",
                "phone": "+998901112233",
                "is_staff": True,
                "is_superuser": True,
                "role": UserRole.ADMIN,
            },
            {
                "username": "admin_dilshod",
                "password": "123",
                "first_name": "Dilshod",
                "last_name": "Rahimov",
                "phone": "+998901112244",
                "is_staff": True,
                "is_superuser": True,
                "role": UserRole.ADMIN,
            },
        ]

        for adm in admins_data:
            user, created = User.objects.get_or_create(
                username=adm["username"],
                defaults={
                    "first_name": adm["first_name"],
                    "last_name": adm["last_name"],
                    "phone": adm["phone"],
                    "is_staff": adm["is_staff"],
                    "is_superuser": adm["is_superuser"],
                    "role": adm["role"],
                },
            )
            user.set_password(adm["password"])
            user.role = adm["role"]
            user.is_staff = adm["is_staff"]
            user.is_superuser = adm["is_superuser"]
            user.save()
            status_text = "yaratildi" if created else "yangilandi"
            self.stdout.write(self.style.SUCCESS(f"Admin: {user.username} ({status_text})"))

        # 2. Kassirlarni yaratish
        cashiers_data = [
            {
                "username": "kassir_ali",
                "password": "123",
                "first_name": "Ali",
                "last_name": "Valiyev",
                "phone": "+998901234501",
            },
            {
                "username": "kassir_nodira",
                "password": "123",
                "first_name": "Nodira",
                "last_name": "Karimova",
                "phone": "+998901234502",
            },
            {
                "username": "kassir_jasur",
                "password": "123",
                "first_name": "Jasur",
                "last_name": "Toshmatov",
                "phone": "+998901234503",
            },
            {
                "username": "kassir_malika",
                "password": "123",
                "first_name": "Malika",
                "last_name": "Sodiqova",
                "phone": "+998901234504",
            },
        ]

        for cash in cashiers_data:
            user, created = User.objects.get_or_create(
                username=cash["username"],
                defaults={
                    "first_name": cash["first_name"],
                    "last_name": cash["last_name"],
                    "phone": cash["phone"],
                    "role": UserRole.CASHIER,
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            user.set_password(cash["password"])
            user.role = UserRole.CASHIER
            user.first_name = cash["first_name"]
            user.last_name = cash["last_name"]
            user.phone = cash["phone"]
            user.save()
            status_text = "yaratildi" if created else "yangilandi"
            self.stdout.write(self.style.SUCCESS(f"Kassir: {user.username} ({status_text})"))

        self.stdout.write(self.style.SUCCESS("Mock ma'lumotlar muvaffaqiyatli to'ldirildi!"))

