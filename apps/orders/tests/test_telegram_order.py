from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, UserRole
from apps.inventory.models import Ingredient, MeasurementUnit
from apps.products.models import Category, Product, ProductRecipe
from apps.orders.models import Order, OrderItem, OrderStatus, OrderType, PaymentType


class TelegramOrderAPITestCase(APITestCase):
    def setUp(self):
        # 1. Kassir
        self.cashier = User.objects.create_user(
            username="kassir_tg",
            password="password123",
            role=UserRole.CASHIER,
        )

        # 2. Xomashyo va Retsept
        self.bun = Ingredient.objects.create(
            name="Burger noni",
            unit=MeasurementUnit.PIECE,
            stock=Decimal("50.000"),
        )
        self.patty = Ingredient.objects.create(
            name="Kotlet",
            unit=MeasurementUnit.PIECE,
            stock=Decimal("50.000"),
        )

        self.category = Category.objects.create(name="Burgerlar", order=1)
        self.burger = Product.objects.create(
            category=self.category,
            name="Telegram Burger",
            price=Decimal("45000.00"),
            is_active=True,
        )

        # Retsept: 1 ta burger = 1 non + 1 kotlet
        ProductRecipe.objects.create(
            product=self.burger,
            ingredient=self.bun,
            quantity=Decimal("1.000")
        )
        ProductRecipe.objects.create(
            product=self.burger,
            ingredient=self.patty,
            quantity=Decimal("1.000")
        )

        self.telegram_order_url = reverse('telegram-order-create')
        self.webapp_url = reverse('webapp:index')

    def test_telegram_order_creation_success(self):
        """
        Telegram WebApp orqali yangi mijoz buyurtma berishi (201 Created).
        Mijoz avtomatik ravishda CUSTOMER roli bilan saqlanadi.
        Boshlang'ich holat: PENDING (Ombor zaxirasiga tegilmaydi).
        """
        payload = {
            "telegram_id": 99887766,
            "first_name": "Sardor",
            "last_name": "Karimov",
            "telegram_username": "sardor_k",
            "phone": "+998901234567",
            "order_type": OrderType.TAKEAWAY,
            "payment_type": PaymentType.CASH,
            "notes": "Piyozsiz",
            "items": [
                {
                    "product_id": self.burger.id,
                    "quantity": 2,
                    "notes": "Issiqroq bo'lsin"
                }
            ]
        }

        # Public so'rov (Token talab qilinmaydi)
        response = self.client.post(self.telegram_order_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], OrderStatus.PENDING)
        self.assertEqual(Decimal(str(response.data['total_price'])), Decimal("90000.00"))
        self.assertEqual(len(response.data['items']), 1)

        # Foydalanuvchi tekshiruvi
        customer = User.objects.filter(telegram_id=99887766).first()
        self.assertIsNotNone(customer)
        self.assertEqual(customer.role, UserRole.CUSTOMER)
        self.assertEqual(customer.first_name, "Sardor")

        # Buyurtma tekshiruvi
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.customer, customer)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertFalse(order.is_stock_deducted)

        # Xomashyo o'zgarmaganligini tekshirish
        self.bun.refresh_from_db()
        self.assertEqual(self.bun.stock, Decimal("50.000"))

    def test_existing_customer_reused_by_telegram_id(self):
        """
        Bir xil telegram_id dan takroriy buyurtma berilganda yangi user ochilmasdan,
        mavjud mijoz qayta ishlatilishi.
        """
        payload = {
            "telegram_id": 55544433,
            "phone": "+998939876543",
            "first_name": "Dilshod",
            "items": [{"product_id": self.burger.id, "quantity": 1}]
        }

        res1 = self.client.post(self.telegram_order_url, payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        users_count_before = User.objects.count()

        # 2-marta shu telegram_id bilan buyurtma
        res2 = self.client.post(self.telegram_order_url, payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

        users_count_after = User.objects.count()
        self.assertEqual(users_count_before, users_count_after)

    def test_telegram_order_validation_errors(self):
        """
        Noto'g'ri payload yuborilganda 400 Bad Request qaytishi.
        """
        # Bo'sh items
        res1 = self.client.post(self.telegram_order_url, {
            "telegram_id": 111,
            "phone": "+998901112233",
            "items": []
        }, format='json')
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)

        # Telefon raqamsiz
        res2 = self.client.post(self.telegram_order_url, {
            "telegram_id": 111,
            "items": [{"product_id": self.burger.id, "quantity": 1}]
        }, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

        # Mavjud bo'lmagan mahsulot ID
        res3 = self.client.post(self.telegram_order_url, {
            "telegram_id": 111,
            "phone": "+998901112233",
            "items": [{"product_id": 99999, "quantity": 1}]
        }, format='json')
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_telegram_order_cashier_accept_and_complete_workflow(self):
        """
        Telegram orqali berilgan buyurtmani kassir qabul qilishi (ACCEPTED)
        va topshirishi (COMPLETED) jarayoni to'liq tekshiruvi.
        """
        payload = {
            "telegram_id": 777666,
            "phone": "+998971112233",
            "first_name": "Aziz",
            "items": [{"product_id": self.burger.id, "quantity": 2}]
        }

        res = self.client.post(self.telegram_order_url, payload, format='json')
        order_id = res.data['id']

        # Kassir qabul qiladi
        self.client.force_authenticate(user=self.cashier)
        accept_url = reverse('cashier-order-accept', kwargs={'pk': order_id})
        res_accept = self.client.post(accept_url)
        self.assertEqual(res_accept.status_code, status.HTTP_200_OK)
        self.assertEqual(res_accept.data['status'], OrderStatus.ACCEPTED)

        # Kassir topshiradi (BOM xomashyolari kamayadi)
        complete_url = reverse('cashier-order-complete', kwargs={'pk': order_id})
        res_complete = self.client.post(complete_url)
        self.assertEqual(res_complete.status_code, status.HTTP_200_OK)
        self.assertEqual(res_complete.data['status'], OrderStatus.COMPLETED)
        self.assertTrue(res_complete.data['is_stock_deducted'])

        # 2 ta burger uchun 2 ta non va 2 ta kotlet kamayishi kerak (50 - 2 = 48)
        self.bun.refresh_from_db()
        self.patty.refresh_from_db()
        self.assertEqual(self.bun.stock, Decimal("48.000"))
        self.assertEqual(self.patty.stock, Decimal("48.000"))

    def test_webapp_page_renders_successfully(self):
        """
        Telegram WebApp HTML sahifasi 200 OK qaytarishi.
        """
        response = self.client.get(self.webapp_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Telegram WebApp")

