from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import UserRole
from apps.inventory.models import Ingredient, MeasurementUnit
from apps.inventory.services import supply_create
from apps.products.models import Category, Product
from apps.products.services import set_product_recipe

User = get_user_model()


class Command(BaseCommand):
    help = "Barcha modellar (Foydalanuvchilar, Xomashyolar, Kirimlar, Menyu va Retseptlar) uchun mock ma'lumotlarni to'ldiradi."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Mock ma'lumotlarni yaratish boshlandi..."))

        # 1. Admin yaratish
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Asosiy",
                "last_name": "Administrator",
                "phone": "+998901112233",
                "is_staff": True,
                "is_superuser": True,
                "role": UserRole.ADMIN,
            },
        )
        admin_user.set_password("123")
        admin_user.role = UserRole.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"Admin tayyor: {admin_user.username}"))

        # 2. Kassir yaratish
        cashier_user, _ = User.objects.get_or_create(
            username="kassir_ali",
            defaults={
                "first_name": "Ali",
                "last_name": "Valiyev",
                "phone": "+998901234501",
                "role": UserRole.CASHIER,
                "is_staff": False,
                "is_superuser": False,
            },
        )
        cashier_user.set_password("123")
        cashier_user.role = UserRole.CASHIER
        cashier_user.save()
        self.stdout.write(self.style.SUCCESS(f"Kassir tayyor: {cashier_user.username}"))

        # 3. Xomashyolar (Ingredients)
        ingredients_info = [
            {"name": "Burger noni", "unit": MeasurementUnit.PIECE, "min_stock": Decimal("30.000")},
            {"name": "Mol go'shti kotleti", "unit": MeasurementUnit.PIECE, "min_stock": Decimal("50.000")},
            {"name": "Tovuq go'shti (file)", "unit": MeasurementUnit.KG, "min_stock": Decimal("10.000")},
            {"name": "Pomidor", "unit": MeasurementUnit.KG, "min_stock": Decimal("5.000")},
            {"name": "Pishloq (Cheddar)", "unit": MeasurementUnit.PIECE, "min_stock": Decimal("40.000")},
            {"name": "Maxsus sous", "unit": MeasurementUnit.KG, "min_stock": Decimal("3.000")},
            {"name": "Lavash xamiri", "unit": MeasurementUnit.PIECE, "min_stock": Decimal("25.000")},
        ]

        ingredients_dict = {}
        for item in ingredients_info:
            ing, _ = Ingredient.objects.get_or_create(
                name=item["name"],
                defaults={"unit": item["unit"], "min_stock": item["min_stock"]}
            )
            ingredients_dict[ing.name] = ing

        self.stdout.write(self.style.SUCCESS(f"{len(ingredients_dict)} ta xomashyo saqlandi."))

        # 4. Kirim qilish (Supplies - Qoldiqni to'ldirish)
        supplies_data = [
            (ingredients_dict["Burger noni"], Decimal("100.000"), Decimal("2500.00")),
            (ingredients_dict["Mol go'shti kotleti"], Decimal("150.000"), Decimal("8000.00")),
            (ingredients_dict["Tovuq go'shti (file)"], Decimal("30.000"), Decimal("45000.00")),
            (ingredients_dict["Pomidor"], Decimal("20.000"), Decimal("12000.00")),
            (ingredients_dict["Pishloq (Cheddar)"], Decimal("100.000"), Decimal("3000.00")),
            (ingredients_dict["Maxsus sous"], Decimal("10.000"), Decimal("25000.00")),
            (ingredients_dict["Lavash xamiri"], Decimal("80.000"), Decimal("2000.00")),
        ]

        for ing, qty, price in supplies_data:
            if ing.stock < Decimal("10.000"):
                supply_create(
                    ingredient=ing,
                    quantity=qty,
                    cost_price=price,
                    supplier="Elit Ta'minot MChJ",
                    notes="Dastlabki zaxira",
                    created_by=admin_user,
                )

        self.stdout.write(self.style.SUCCESS("Omborga kirimlar qilindi va qoldiqlar to'ldirildi."))

        # 5. Menyu Kategoriyalari
        cat_burger, _ = Category.objects.get_or_create(name="Burgerlar", defaults={"order": 1})
        cat_lavash, _ = Category.objects.get_or_create(name="Lavashlar", defaults={"order": 2})

        # 6. Tayyor Mahsulotlar (Products)
        p_chizburger, _ = Product.objects.get_or_create(
            category=cat_burger,
            name="Chizburger",
            defaults={"price": Decimal("35000.00"), "description": "Shirali go'sht va pishloqli klassik burger"}
        )

        p_double_burger, _ = Product.objects.get_or_create(
            category=cat_burger,
            name="Double Burger",
            defaults={"price": Decimal("48000.00"), "description": "Ikkitalik go'sht va qo'shaloq pishloqli burger"}
        )

        p_lavash, _ = Product.objects.get_or_create(
            category=cat_lavash,
            name="Tovuqli Lavash",
            defaults={"price": Decimal("32000.00"), "description": "Tovuq go'shti, pomidor va sousli lavash"}
        )

        # 7. Retseptlarni bog'lash (Recipes / BOM)
        # Chizburger: 1x non, 1x kotlet, 1x pishloq, 0.030 kg pomidor, 0.020 kg sous
        set_product_recipe(p_chizburger, [
            {"ingredient_id": ingredients_dict["Burger noni"].id, "quantity": Decimal("1.000")},
            {"ingredient_id": ingredients_dict["Mol go'shti kotleti"].id, "quantity": Decimal("1.000")},
            {"ingredient_id": ingredients_dict["Pishloq (Cheddar)"].id, "quantity": Decimal("1.000")},
            {"ingredient_id": ingredients_dict["Pomidor"].id, "quantity": Decimal("0.030")},
            {"ingredient_id": ingredients_dict["Maxsus sous"].id, "quantity": Decimal("0.020")},
        ])

        # Double Burger: 1x non, 2x kotlet, 2x pishloq, 0.050 kg pomidor, 0.030 kg sous
        set_product_recipe(p_double_burger, [
            {"ingredient_id": ingredients_dict["Burger noni"].id, "quantity": Decimal("1.000")},
            {"ingredient_id": ingredients_dict["Mol go'shti kotleti"].id, "quantity": Decimal("2.000")},
            {"ingredient_id": ingredients_dict["Pishloq (Cheddar)"].id, "quantity": Decimal("2.000")},
            {"ingredient_id": ingredients_dict["Pomidor"].id, "quantity": Decimal("0.050")},
            {"ingredient_id": ingredients_dict["Maxsus sous"].id, "quantity": Decimal("0.030")},
        ])

        # Tovuqli Lavash: 1x lavash xamiri, 0.150 kg tovuq file, 0.040 kg pomidor, 0.030 kg sous
        set_product_recipe(p_lavash, [
            {"ingredient_id": ingredients_dict["Lavash xamiri"].id, "quantity": Decimal("1.000")},
            {"ingredient_id": ingredients_dict["Tovuq go'shti (file)"].id, "quantity": Decimal("0.150")},
            {"ingredient_id": ingredients_dict["Pomidor"].id, "quantity": Decimal("0.040")},
            {"ingredient_id": ingredients_dict["Maxsus sous"].id, "quantity": Decimal("0.030")},
        ])

        self.stdout.write(self.style.SUCCESS("Barcha mahsulotlar va retseptlar (BOM) muvaffaqiyatli saqlandi!"))
        self.stdout.write(self.style.SUCCESS("Mock ma'lumotlar to'liq va muvaffaqiyatli kiritildi!"))
