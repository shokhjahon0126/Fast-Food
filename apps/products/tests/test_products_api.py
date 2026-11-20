from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, UserRole
from apps.inventory.models import Ingredient, MeasurementUnit
from apps.products.models import Category, Product, ProductRecipe


class ProductsAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_prod",
            password="password123",
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.cashier = User.objects.create_user(
            username="cashier_prod",
            password="password123",
            role=UserRole.CASHIER,
        )

        self.category = Category.objects.create(name="Burgerlar", order=1)

        self.bun = Ingredient.objects.create(name="Burger noni", unit=MeasurementUnit.PIECE, stock=Decimal("50"))
        self.patty = Ingredient.objects.create(name="Kotlet", unit=MeasurementUnit.PIECE, stock=Decimal("80"))
        self.tomato = Ingredient.objects.create(name="Pomidor", unit=MeasurementUnit.KG, stock=Decimal("15"))

        self.burger = Product.objects.create(
            category=self.category,
            name="Mega Burger",
            price=Decimal("42000.00"),
        )

        self.products_url = reverse("product-list")
        self.categories_url = reverse("category-list")

    def test_set_recipe_for_product(self):
        """Admin mahsulot uchun retseptni (BOM) to'liq sozlay olishi kerak."""
        self.client.force_authenticate(user=self.admin)
        url = reverse("product-set-recipe", kwargs={"pk": self.burger.id})
        data = {
            "items": [
                {"ingredient_id": self.bun.id, "quantity": "1.000"},
                {"ingredient_id": self.patty.id, "quantity": "2.000"},
                {"ingredient_id": self.tomato.id, "quantity": "0.050"},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self.assertEqual(self.burger.recipes.count(), 3)
        bun_recipe = self.burger.recipes.get(ingredient=self.bun)
        self.assertEqual(bun_recipe.quantity, Decimal("1.000"))

    def test_cashier_cannot_set_recipe(self):
        """Kassir retseptni o'zgartira olmasligi kerak (403)."""
        self.client.force_authenticate(user=self.cashier)
        url = reverse("product-set-recipe", kwargs={"pk": self.burger.id})
        data = {
            "items": [{"ingredient_id": self.bun.id, "quantity": "1.000"}]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_products_list_no_n_plus_one(self):
        """Mahsulotlar va ularning retseptlari yuklanganda N+1 so'rov bo'lmasligi kerak."""
        self.client.force_authenticate(user=self.cashier)

        # 5 ta mahsulot va har biriga retsept yaratamiz
        for i in range(5):
            prod = Product.objects.create(
                category=self.category,
                name=f"Burger {i}",
                price=Decimal("30000.00"),
            )
            ProductRecipe.objects.create(product=prod, ingredient=self.bun, quantity=Decimal("1.000"))
            ProductRecipe.objects.create(product=prod, ingredient=self.patty, quantity=Decimal("1.000"))

        # select_related('category') va prefetch_related('recipes__ingredient')
        # bilan SQL so'rovlar soni qat'iy nazorat qilinadi:
        # 1: count query (pagination)
        # 2: product list with category (select_related)
        # 3: recipes for all products (prefetch_related)
        # 4: ingredients for all recipes (prefetch_related)
        with self.assertNumQueries(4):
            response = self.client.get(self.products_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertGreaterEqual(response.data["count"], 5)

