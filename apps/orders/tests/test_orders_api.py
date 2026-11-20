from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, UserRole
from apps.inventory.models import Ingredient, MeasurementUnit
from apps.products.models import Category, Product, ProductRecipe
from apps.orders.models import Order, OrderStatus, OrderType


class OrdersAPITestCase(APITestCase):
    def setUp(self):
        # 1. Users
        self.admin = User.objects.create_user(
            username="admin_order",
            password="password123",
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.cashier = User.objects.create_user(
            username="cashier_order",
            password="password123",
            role=UserRole.CASHIER,
        )
        self.customer = User.objects.create_user(
            username="customer_order",
            password="password123",
            first_name="Bobur",
            phone="+998901119988",
            role=UserRole.CUSTOMER,
        )

        # 2. Xomashyolar (Ombor)
        self.bun = Ingredient.objects.create(
            name="Burger noni",
            unit=MeasurementUnit.PIECE,
            stock=Decimal("50.000"),
        )
        self.patty = Ingredient.objects.create(
            name="Mol go'shti kotleti",
            unit=MeasurementUnit.PIECE,
            stock=Decimal("100.000"),
        )

        # 3. Kategoriya va Mahsulot
        self.category = Category.objects.create(name="Burgerlar", order=1)
        self.burger = Product.objects.create(
            category=self.category,
            name="Big Burger",
            price=Decimal("40000.00"),
        )

        # 4. Retsept (1 ta burger = 1 non, 2 kotlet)
        ProductRecipe.objects.create(product=self.burger, ingredient=self.bun, quantity=Decimal("1.000"))
        ProductRecipe.objects.create(product=self.burger, ingredient=self.patty, quantity=Decimal("2.000"))

        # URLs
        self.menu_url = reverse("product-list")
        self.register_url = reverse("register")
        self.my_orders_url = reverse("customer-order-list")
        self.cashier_orders_url = reverse("cashier-order-list")

    # --- 1. Ochiq Menyu va Ro'yxatdan O'tish ---

    def test_public_user_can_view_menu_without_auth(self):
        """Mehmon (login qilmagan) foydalanuvchi menyuni ko'ra olishi kerak."""
        response = self.client.get(self.menu_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_public_user_can_register_as_customer(self):
        """Mehmon ro'yxatdan o'tib mijoz bo'la olishi kerak (rol avtomatik customer bo'ladi)."""
        data = {
            "username": "new_client",
            "password": "secret_password",
            "first_name": "Sardor",
            "phone": "+998909998877",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], UserRole.CUSTOMER)

        user = User.objects.get(username="new_client")
        self.assertEqual(user.role, UserRole.CUSTOMER)
        self.assertFalse(user.is_staff)

    # --- 2. Buyurtma Berish va Ombor Logikasi ---

    def test_customer_can_create_order_pending_does_not_deduct_stock(self):
        """Mijoz buyurtma beradi (PENDING), bu paytda ombordagi xomashyo kamaymaydi."""
        self.client.force_authenticate(user=self.customer)
        data = {
            "items": [{"product_id": self.burger.id, "quantity": 3}],
            "order_type": OrderType.TAKEAWAY,
            "notes": "Tezroq iltimos",
        }
        response = self.client.post(self.my_orders_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], OrderStatus.PENDING)
        self.assertEqual(response.data["total_price"], "120000.00")

        # Ombordagi qoldiq o'zgarmasligi kerak!
        self.bun.refresh_from_db()
        self.patty.refresh_from_db()
        self.assertEqual(self.bun.stock, Decimal("50.000"))
        self.assertEqual(self.patty.stock, Decimal("100.000"))

    def test_cashier_accept_order_does_not_deduct_stock(self):
        """Kassir buyurtmani qabul qiladi (ACCEPTED), bu paytda ham ombor qoldig'i kamaymaydi!"""
        # Avval buyurtma yaratamiz
        self.client.force_authenticate(user=self.customer)
        create_resp = self.client.post(
            self.my_orders_url,
            {"items": [{"product_id": self.burger.id, "quantity": 2}]},
            format="json"
        )
        order_id = create_resp.data["id"]

        # Kassir qabul qiladi
        self.client.force_authenticate(user=self.cashier)
        accept_url = reverse("cashier-order-accept", kwargs={"pk": order_id})
        accept_resp = self.client.post(accept_url)
        self.assertEqual(accept_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(accept_resp.data["status"], OrderStatus.ACCEPTED)

        # Ombordagi qoldiq hali ham o'zgarmasligi shart!
        self.bun.refresh_from_db()
        self.patty.refresh_from_db()
        self.assertEqual(self.bun.stock, Decimal("50.000"))
        self.assertEqual(self.patty.stock, Decimal("100.000"))

    def test_cashier_complete_order_deducts_inventory_stock(self):
        """Buyurtma mijozga TOPSHIRILGANDA (COMPLETED), ombordagi xomashyo retsept bo'yicha kamayishi kerak!"""
        # 1. Buyurtma berish (2 ta Big Burger)
        self.client.force_authenticate(user=self.customer)
        create_resp = self.client.post(
            self.my_orders_url,
            {"items": [{"product_id": self.burger.id, "quantity": 2}]},
            format="json"
        )
        order_id = create_resp.data["id"]

        # 2. Kassir qabul qiladi
        self.client.force_authenticate(user=self.cashier)
        accept_url = reverse("cashier-order-accept", kwargs={"pk": order_id})
        self.client.post(accept_url)

        # 3. Buyurtma topshirildi (Complete)
        complete_url = reverse("cashier-order-complete", kwargs={"pk": order_id})
        complete_resp = self.client.post(complete_url)
        self.assertEqual(complete_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(complete_resp.data["status"], OrderStatus.COMPLETED)
        self.assertTrue(complete_resp.data["is_stock_deducted"])

        # 4. Ombor qoldig'ini tekshirish:
        # 2 ta burger uchun:
        # 2 * 1 non = 2 non kamayishi kerak: 50.000 - 2 = 48.000
        # 2 * 2 kotlet = 4 kotlet kamayishi kerak: 100.000 - 4 = 96.000
        self.bun.refresh_from_db()
        self.patty.refresh_from_db()
        self.assertEqual(self.bun.stock, Decimal("48.000"))
        self.assertEqual(self.patty.stock, Decimal("96.000"))

    # --- 3. Ruxsatlar va Xavfsizlik ---

    def test_customer_cannot_accept_or_complete_order(self):
        """Mijoz kassirning buyurtmani qabul qilish yoki topshirish endpointiga kira olmasligi kerak (403)."""
        self.client.force_authenticate(user=self.customer)
        accept_url = reverse("cashier-order-accept", kwargs={"pk": 1})
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_create_order(self):
        """Mehmon (login qilmagan) foydalanuvchi buyurtma bera olmasligi kerak (401)."""
        response = self.client.post(self.my_orders_url, {"items": []}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- 4. N+1 Query Nazorati ---

    def test_cashier_orders_list_no_n_plus_one(self):
        """Kassir navbatidagi buyurtmalar ro'yxati minimal so'rovlar bilan yuklanishi kerak."""
        self.client.force_authenticate(user=self.cashier)

        # 5 ta buyurtma yaratamiz
        for i in range(5):
            order = Order.objects.create(
                customer=self.customer,
                total_price=Decimal("40000.00"),
                status=OrderStatus.PENDING,
            )
            order.items.create(product=self.burger, quantity=1, unit_price=self.burger.price)

        # items_prefetch yordamida buyurtmalar, mijozlar va barcha mahsulotlar
        # kategoriyalari bilan atigi 3 ta SQL so'rovda yuklanadi:
        with self.assertNumQueries(3):
            response = self.client.get(self.cashier_orders_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

