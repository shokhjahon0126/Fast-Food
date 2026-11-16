from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, UserRole


class UsersAPITestCase(APITestCase):
    def setUp(self):
        # 1. Admin yaratish
        self.admin = User.objects.create_user(
            username="test_admin",
            password="admin_password123",
            first_name="Admin",
            last_name="One",
            phone="+998901111111",
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        # 2. Boshqa Admin yaratish
        self.other_admin = User.objects.create_user(
            username="test_admin_two",
            password="admin_password123",
            first_name="Admin",
            last_name="Two",
            phone="+998902222222",
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        # 3. Kassir yaratish
        self.cashier = User.objects.create_user(
            username="test_cashier",
            password="cashier_password123",
            first_name="Kassir",
            last_name="Baland",
            phone="+998903333333",
            role=UserRole.CASHIER,
            is_staff=False,
            is_superuser=False,
        )

        self.cashiers_list_url = reverse("cashier-list")
        self.profile_url = reverse("user-profile")
        self.login_url = reverse("login")

    # --- 0. Login Qilinganda ID va Role Qaytishi ---

    def test_admin_login_returns_id_and_role(self):
        """Admin login qilganda id va role to'g'ri qaytishi kerak."""
        data = {
            "username": "test_admin",
            "password": "admin_password123",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["id"], self.admin.id)
        self.assertEqual(response.data["role"], UserRole.ADMIN)

    def test_cashier_login_returns_id_and_role(self):
        """Kassir login qilganda id va role to'g'ri qaytishi kerak."""
        data = {
            "username": "test_cashier",
            "password": "cashier_password123",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["id"], self.cashier.id)
        self.assertEqual(response.data["role"], UserRole.CASHIER)

    # --- 1. Admin Kassir Yaratish va Cheklovlar ---

    def test_admin_can_create_cashier(self):
        """Admin yangi kassir yarata olishi kerak."""
        self.client.force_authenticate(user=self.admin)
        data = {
            "username": "new_cashier",
            "password": "valid_password_123",
            "first_name": "Yangi",
            "last_name": "Kassir",
            "phone": "+998904444444",
        }
        response = self.client.post(self.cashiers_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "new_cashier")
        self.assertEqual(response.data["role"], UserRole.CASHIER)

        new_user = User.objects.get(username="new_cashier")
        self.assertEqual(new_user.role, UserRole.CASHIER)
        self.assertFalse(new_user.is_staff)

    def test_cannot_create_admin_via_api(self):
        """API orqali Admin rolidagi foydalanuvchi yaratish imkoni bo'lmasligi kerak."""
        self.client.force_authenticate(user=self.admin)
        data = {
            "username": "fake_admin",
            "password": "valid_password_123",
            "role": "admin",
        }
        response = self.client.post(self.cashiers_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Roli baribir cashier bo'lishi shart!
        self.assertEqual(response.data["role"], UserRole.CASHIER)
        created_user = User.objects.get(username="fake_admin")
        self.assertEqual(created_user.role, UserRole.CASHIER)
        self.assertFalse(created_user.is_superuser)

    # --- 2. O'chirish Cheklovlari (Admin O'zini va Sherigini O'chira Olmaydi) ---

    def test_admin_cannot_delete_self(self):
        """Admin o'zining shaxsiy hisobini o'chira olmasligi kerak."""
        self.client.force_authenticate(user=self.admin)
        url = reverse("cashier-detail", kwargs={"pk": self.admin.id})
        response = self.client.delete(url)
        # Admin kassirlar ro'yxatida bo'lmagani uchun yoki delete cheklovi bo'yicha bloklanadi (404/400)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
        self.assertTrue(User.objects.filter(id=self.admin.id).exists())

    def test_admin_cannot_delete_another_admin(self):
        """Admin boshqa admin hisobini o'chira olmasligi kerak."""
        self.client.force_authenticate(user=self.admin)
        url = reverse("cashier-detail", kwargs={"pk": self.other_admin.id})
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
        self.assertTrue(User.objects.filter(id=self.other_admin.id).exists())

    def test_admin_can_delete_cashier(self):
        """Admin kassirni muvaffaqiyatli o'chira olishi kerak."""
        self.client.force_authenticate(user=self.admin)
        url = reverse("cashier-detail", kwargs={"pk": self.cashier.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.cashier.id).exists())

    # --- 3. Kassir Huquqlari va Cheklovlari ---

    def test_cashier_cannot_access_cashiers_list(self):
        """Kassir boshqa kassirlar ro'yxatini ko'ra olmasligi kerak (403)."""
        self.client.force_authenticate(user=self.cashier)
        response = self.client.get(self.cashiers_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cashier_cannot_create_cashier(self):
        """Kassir yangi kassir qo'sha olmasligi kerak (403)."""
        self.client.force_authenticate(user=self.cashier)
        data = {
            "username": "cashier_attempt",
            "password": "valid_password_123",
        }
        response = self.client.post(self.cashiers_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cashier_cannot_change_own_role(self):
        """Kassir o'z rolini update qila olmasligi kerak."""
        self.client.force_authenticate(user=self.cashier)
        response = self.client.patch(self.profile_url, {"role": "admin"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Rol o'zgarmasligi kerak!
        self.cashier.refresh_from_db()
        self.assertEqual(self.cashier.role, UserRole.CASHIER)

    def test_cashier_can_update_own_profile(self):
        """Kassir o'z shaxsiy ma'lumotlarini o'zgartira olishi kerak."""
        self.client.force_authenticate(user=self.cashier)
        data = {
            "first_name": "Alisher",
            "last_name": "Yangi",
            "phone": "+998905555555",
        }
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cashier.refresh_from_db()
        self.assertEqual(self.cashier.first_name, "Alisher")
        self.assertEqual(str(self.cashier.phone), "+998905555555")

    # --- 4. N+1 Query Nazorati ---

    def test_no_n_plus_one_on_cashiers_list(self):
        """Kassirlar ro'yxatini olishda so'rovlar soni optimal bo'lishi kerak."""
        self.client.force_authenticate(user=self.admin)
        # 10 ta yangi kassir yaratamiz
        bulk_cashiers = [
            User(
                username=f"bulk_cashier_{i}",
                first_name=f"Name {i}",
                role=UserRole.CASHIER,
            )
            for i in range(10)
        ]
        User.objects.bulk_create(bulk_cashiers)

        # So'rovlar sonini nazorat qilish (pagination count + query)
        with self.assertNumQueries(2):
            response = self.client.get(self.cashiers_list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

