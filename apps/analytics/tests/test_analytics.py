from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User, UserRole
from apps.products.models import Category, Product
from apps.orders.models import Order, OrderItem, OrderStatus, OrderType, PaymentType


class AnalyticsAPITestCase(APITestCase):
    def setUp(self):
        # 1. Foydalanuvchilar (Admin, Kassir, Mijoz)
        self.admin = User.objects.create_user(
            username="admin_analytics",
            password="password123",
            role=UserRole.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.cashier = User.objects.create_user(
            username="cashier_analytics",
            password="password123",
            role=UserRole.CASHIER,
        )
        self.customer = User.objects.create_user(
            username="customer_analytics",
            password="password123",
            role=UserRole.CUSTOMER,
        )

        # 2. Kategoriyalar va Mahsulotlar
        self.burger_cat = Category.objects.create(name="Burgerlar", order=1)
        self.drinks_cat = Category.objects.create(name="Ichimliklar", order=2)

        self.burger = Product.objects.create(
            category=self.burger_cat,
            name="Max Burger",
            price=Decimal("40000.00"),
            is_active=True,
        )
        self.cola = Product.objects.create(
            category=self.drinks_cat,
            name="Koka Kola 0.5L",
            price=Decimal("10000.00"),
            is_active=True,
        )
        self.tea = Product.objects.create(
            category=self.drinks_cat,
            name="Ko'k choy",
            price=Decimal("5000.00"),
            is_active=True,
        )

        # 3. URL lar
        self.dashboard_url = reverse('analytics:dashboard-overview')
        self.ranking_url = reverse('analytics:products-ranking')
        self.trend_url = reverse('analytics:sales-trend')

    def test_anonymous_cannot_access_analytics(self):
        """
        Anonim foydalanuvchi tahliliy endpointlarga kira olmaydi (401).
        """
        res1 = self.client.get(self.dashboard_url)
        self.assertEqual(res1.status_code, status.HTTP_401_UNAUTHORIZED)

        res2 = self.client.get(self.ranking_url)
        self.assertEqual(res2.status_code, status.HTTP_401_UNAUTHORIZED)

        res3 = self.client.get(self.trend_url)
        self.assertEqual(res3.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_and_cashier_forbidden(self):
        """
        Mijoz va Kassir rollariga dashboard ruxsat etilmagan (403 Forbidden).
        """
        for user in [self.customer, self.cashier]:
            self.client.force_authenticate(user=user)

            res1 = self.client.get(self.dashboard_url)
            self.assertEqual(res1.status_code, status.HTTP_403_FORBIDDEN)

            res2 = self.client.get(self.ranking_url)
            self.assertEqual(res2.status_code, status.HTTP_403_FORBIDDEN)

            res3 = self.client.get(self.trend_url)
            self.assertEqual(res3.status_code, status.HTTP_403_FORBIDDEN)

    def test_empty_database_analytics(self):
        """
        Ma'lumotlar bazasida hech qanday buyurtma bo'lmaganda
        xatoliksiz 0.00 tushum va 0 buyurtma soni qaytishi.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['daily']['revenue'], '0.00')
        self.assertEqual(response.data['daily']['orders_count'], 0)
        self.assertEqual(response.data['order_statuses']['total'], 0)
        self.assertEqual(response.data['all_time_revenue'], '0.00')

    def test_dashboard_overview_metrics_accuracy(self):
        """
        Daromad, buyurtmalar soni va mahsulotlar reytingi aniq hisoblanishi:
        - Faqat COMPLETED buyurtmalar daromadga qo'shiladi.
        - CANCELLED buyurtmalar yo'qotilgan summa sifatida aks etadi.
        - PENDING va ACCEPTED buyurtmalar status taqsimotida ko'rinadi.
        """
        # Order 1: COMPLETED (2 Max Burger + 1 Cola = 90,000 so'm)
        o1 = Order.objects.create(
            customer=self.customer,
            status=OrderStatus.COMPLETED,
            order_type=OrderType.DINE_IN,
            payment_type=PaymentType.CASH,
            total_price=Decimal("90000.00"),
        )
        OrderItem.objects.create(
            order=o1,
            product=self.burger,
            quantity=2,
            unit_price=self.burger.price,
            total_price=Decimal("80000.00"),
        )
        OrderItem.objects.create(
            order=o1,
            product=self.cola,
            quantity=1,
            unit_price=self.cola.price,
            total_price=Decimal("10000.00"),
        )

        # Order 2: CANCELLED (1 Max Burger = 40,000 so'm)
        o2 = Order.objects.create(
            customer=self.customer,
            status=OrderStatus.CANCELLED,
            order_type=OrderType.TAKEAWAY,
            payment_type=PaymentType.CASH,
            total_price=Decimal("40000.00"),
        )
        OrderItem.objects.create(
            order=o2,
            product=self.burger,
            quantity=1,
            unit_price=self.burger.price,
            total_price=Decimal("40000.00"),
        )

        # Order 3: PENDING (1 Ko'k choy = 5,000 so'm)
        Order.objects.create(
            customer=self.customer,
            status=OrderStatus.PENDING,
            order_type=OrderType.DINE_IN,
            payment_type=PaymentType.CARD,
            total_price=Decimal("5000.00"),
        )

        # Order 4: ACCEPTED (1 Max Burger = 40,000 so'm)
        Order.objects.create(
            customer=self.customer,
            status=OrderStatus.ACCEPTED,
            order_type=OrderType.DINE_IN,
            payment_type=PaymentType.CASH,
            total_price=Decimal("40000.00"),
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Daromad tekshiruvi: Faqat COMPLETED buyurtma hisoblandi
        self.assertEqual(response.data['daily']['revenue'], '90000.00')
        self.assertEqual(response.data['daily']['orders_count'], 1)
        self.assertEqual(response.data['weekly']['revenue'], '90000.00')
        self.assertEqual(response.data['monthly']['revenue'], '90000.00')
        self.assertEqual(response.data['all_time_revenue'], '90000.00')

        # Statuslar tekshiruvi
        statuses = response.data['order_statuses']
        self.assertEqual(statuses['completed'], 1)
        self.assertEqual(statuses['cancelled'], 1)
        self.assertEqual(statuses['pending'], 1)
        self.assertEqual(statuses['accepted'], 1)
        self.assertEqual(statuses['total'], 4)
        self.assertEqual(statuses['cancelled_revenue_loss'], '40000.00')

        # Top va Past mahsulotlar tekshiruvi
        top_products = response.data['top_selling_products']
        self.assertEqual(top_products[0]['name'], "Max Burger")
        self.assertEqual(top_products[0]['total_sold_quantity'], 2)
        self.assertEqual(top_products[0]['total_revenue'], '80000.00')

        least_products = response.data['least_selling_products']
        # Ko'k choy umuman COMPLETED buyurtmada sotilmagan, shuning uchun 0
        self.assertEqual(least_products[0]['name'], "Ko'k choy")
        self.assertEqual(least_products[0]['total_sold_quantity'], 0)

    def test_product_sales_ranking_ordering_and_filters(self):
        """
        Mahsulotlar reytingida saralash (ordering) va filtrlash to'g'ri ishlashi.
        """
        # COMPLETED buyurtma
        o = Order.objects.create(
            customer=self.customer,
            status=OrderStatus.COMPLETED,
            total_price=Decimal("90000.00"),
        )
        OrderItem.objects.create(
            order=o,
            product=self.burger,
            quantity=5,
            unit_price=self.burger.price,
            total_price=Decimal("200000.00"),
        )
        OrderItem.objects.create(
            order=o,
            product=self.cola,
            quantity=2,
            unit_price=self.cola.price,
            total_price=Decimal("20000.00"),
        )

        self.client.force_authenticate(user=self.admin)

        # 1. Kamayish tartibida saralash (-total_sold_quantity)
        res_desc = self.client.get(f"{self.ranking_url}?ordering=-total_sold_quantity")
        self.assertEqual(res_desc.status_code, status.HTTP_200_OK)
        results = res_desc.data['results']
        self.assertEqual(results[0]['name'], "Max Burger")
        self.assertEqual(results[0]['total_sold_quantity'], 5)
        self.assertEqual(results[1]['name'], "Koka Kola 0.5L")
        self.assertEqual(results[1]['total_sold_quantity'], 2)

        # 2. O'sish tartibida saralash (total_sold_quantity)
        res_asc = self.client.get(f"{self.ranking_url}?ordering=total_sold_quantity")
        self.assertEqual(res_asc.status_code, status.HTTP_200_OK)
        results_asc = res_asc.data['results']
        self.assertEqual(results_asc[0]['name'], "Ko'k choy")
        self.assertEqual(results_asc[0]['total_sold_quantity'], 0)

        # 3. Kategoriya bo'yicha filtrlash
        res_cat = self.client.get(f"{self.ranking_url}?category={self.drinks_cat.id}")
        self.assertEqual(res_cat.status_code, status.HTTP_200_OK)
        for prod in res_cat.data['results']:
            self.assertEqual(prod['category_id'], self.drinks_cat.id)

    def test_sales_trend_view(self):
        """
        Kunlik sotuv trendi grafigi ma'lumotlari to'g'ri shakllanishi.
        """
        Order.objects.create(
            customer=self.customer,
            status=OrderStatus.COMPLETED,
            total_price=Decimal("50000.00"),
        )

        self.client.force_authenticate(user=self.admin)
        res = self.client.get(f"{self.trend_url}?days=7")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)
        self.assertEqual(res.data[-1]['total_revenue'], '50000.00')
        self.assertEqual(res.data[-1]['orders_count'], 1)

    def test_sales_trend_negative_date_validation(self):
        """
        start_date > end_date bo'lganda 400 Bad Request qaytishi.
        """
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(f"{self.trend_url}?start_date=2026-12-01&end_date=2026-11-01")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', res.data)

    def test_analytics_database_queries_no_n_plus_one(self):
        """
        N+1 muammosi yo'qligini tekshirish.
        Ko'plab mahsulot va buyurtmalar mavjud bo'lganda ham so'rovlar soni kam va qat'iy saqlanishi kerak.
        """
        self.client.force_authenticate(user=self.admin)

        # Dashboard barcha ma'lumotlarni 4-5 ta tezkor so'rovda qaytarishi kerak
        with self.assertNumQueries(3):
            res = self.client.get(self.dashboard_url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

