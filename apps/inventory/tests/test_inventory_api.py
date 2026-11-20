from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, UserRole
from apps.inventory.models import Ingredient, Supply, MeasurementUnit


class InventoryAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_test",
            password="password123",
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.cashier = User.objects.create_user(
            username="cashier_test",
            password="password123",
            role=UserRole.CASHIER,
        )

        self.meat = Ingredient.objects.create(
            name="Mol go'shti",
            unit=MeasurementUnit.KG,
            stock=Decimal("5.000"),
            min_stock=Decimal("2.000"),
        )

        self.ingredients_url = reverse("ingredient-list")
        self.supplies_url = reverse("supply-list")

    def test_authenticated_can_list_ingredients(self):
        """Autentifikatsiyadan o'tgan foydalanuvchi xomashyolarni ko'ra olishi kerak."""
        self.client.force_authenticate(user=self.cashier)
        response = self.client.get(self.ingredients_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_supply_creation_increases_ingredient_stock(self):
        """Omborga kirim qilinganda xomashyo qoldig'i avtomatik oshishi kerak."""
        self.client.force_authenticate(user=self.admin)
        data = {
            "ingredient_id": self.meat.id,
            "quantity": "10.000",
            "cost_price": "65000.00",
            "supplier": "Go'sht Savdo MChJ",
        }
        response = self.client.post(self.supplies_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 5.000 + 10.000 = 15.000 kg bo'lishi shart!
        self.meat.refresh_from_db()
        self.assertEqual(self.meat.stock, Decimal("15.000"))

        supply = Supply.objects.get(id=response.data["id"])
        self.assertEqual(supply.total_price, Decimal("650000.00"))

    def test_cashier_cannot_create_supply(self):
        """Kassir kirim qila olmasligi kerak (403)."""
        self.client.force_authenticate(user=self.cashier)
        data = {
            "ingredient_id": self.meat.id,
            "quantity": "5.000",
            "cost_price": "50000.00",
        }
        response = self.client.post(self.supplies_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_negative_quantity_supply_rejected(self):
        """Manfiy yoki 0 miqdorli kirim rad etilishi kerak."""
        self.client.force_authenticate(user=self.admin)
        data = {
            "ingredient_id": self.meat.id,
            "quantity": "-5.000",
            "cost_price": "50000.00",
        }
        response = self.client.post(self.supplies_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_direct_supply_save_increases_stock_in_admin(self):
        """Django Admin orqali Supply yaratilganda Ingredient qoldig'i avtomatik oshishi kerak."""
        initial_stock = self.meat.stock  # 5.000
        supply = Supply.objects.create(
            ingredient=self.meat,
            quantity=Decimal("8.000"),
            cost_price=Decimal("60000.00"),
            supplier="Admin orqali ta'minot",
            created_by=self.admin,
        )
        self.meat.refresh_from_db()
        self.assertEqual(self.meat.stock, initial_stock + Decimal("8.000"))

    def test_supply_deletion_decreases_stock(self):
        """Kirim o'chirilganda xomashyo qoldig'i mos ravishda kamayishi kerak."""
        supply = Supply.objects.create(
            ingredient=self.meat,
            quantity=Decimal("10.000"),
            cost_price=Decimal("60000.00"),
        )
        self.meat.refresh_from_db()
        self.assertEqual(self.meat.stock, Decimal("15.000"))

        supply.delete()
        self.meat.refresh_from_db()
        self.assertEqual(self.meat.stock, Decimal("5.000"))

