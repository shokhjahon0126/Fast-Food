from decimal import Decimal
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError
from apps.products.models import Product
from apps.inventory.models import Ingredient
from apps.orders.models import Order, OrderItem, OrderStatus, OrderType, PaymentType


@transaction.atomic
def order_create(
    *,
    customer,
    items_data: list[dict],
    order_type: str = OrderType.TAKEAWAY,
    payment_type: str = PaymentType.CASH,
    delivery_address: str = "",
    notes: str = "",
) -> Order:
    """
    Yangi buyurtma yaratish biznes mantiqi.
    Boshlang'ich holat: PENDING (Kutilmoqda).
    Bu bosqichda ombor qoldig'iga tegilmaydi.
    """
    if not items_data:
        raise ValidationError({"items": "Buyurtmada kamida bitta mahsulot bo'lishi shart."})

    product_ids = [item['product_id'] for item in items_data]
    products_map = {p.id: p for p in Product.objects.filter(id__in=product_ids, is_active=True)}

    for item in items_data:
        p_id = item['product_id']
        qty = item.get('quantity', 1)

        if p_id not in products_map:
            raise ValidationError({"product_id": f"ID={p_id} bo'lgan faol mahsulot topilmadi."})

        if int(qty) <= 0:
            raise ValidationError({"quantity": "Mahsulot miqdori 1 dan kam bo'lishi mumkin emas."})

    order = Order.objects.create(
        customer=customer,
        order_type=order_type,
        payment_type=payment_type,
        delivery_address=delivery_address if order_type == OrderType.DELIVERY else "",
        notes=notes,
        status=OrderStatus.PENDING,
        total_price=Decimal('0.00'),
    )

    total_amount = Decimal('0.00')
    order_items = []

    for item in items_data:
        product = products_map[item['product_id']]
        quantity = int(item['quantity'])
        unit_price = product.price
        item_total = unit_price * Decimal(quantity)
        total_amount += item_total

        order_items.append(
            OrderItem(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=item_total,
                notes=item.get('notes', ''),
            )
        )

    OrderItem.objects.bulk_create(order_items)
    order.total_price = total_amount
    order.save(update_fields=['total_price'])

    return order


def order_accept(*, order: Order, cashier_user) -> Order:
    """
    Kassir buyurtmani qabul qilishi (Status: ACCEPTED).
    Talabga ko'ra, bu bosqichda ombordagi xomashyo hali KAMAYMAYDI!
    Faqatgina buyurtma oshxonaga tayyorlash uchun yuboriladi.
    """
    if order.status != OrderStatus.PENDING:
        raise ValidationError({"detail": "Faqat yangi (kutilayotgan) buyurtmalarni qabul qilish mumkin."})

    order.status = OrderStatus.ACCEPTED
    order.accepted_by = cashier_user
    order.save(update_fields=['status', 'accepted_by', 'updated_at'])
    return order


@transaction.atomic
def order_complete(*, order: Order, cashier_user=None) -> Order:
    """
    Buyurtma tayyor bo'lib, mijozga TOPSHIRILGANDA (Status: COMPLETED) chaqiriladi.
    AYNAN SHU BOSQICHDA taomlarning retsepti (ProductRecipe) bo'yicha
    ombordagi barcha kerakli xomashyolar (Ingredient.stock) avtomatik ayirib tashlanadi (chiqim qilinadi).
    """
    if order.status != OrderStatus.ACCEPTED:
        raise ValidationError({"detail": "Faqat qabul qilingan (ACCEPTED) buyurtmalarni topshirish mumkin."})

    if not order.is_stock_deducted:
        # Buyurtmadagi barcha taomlar va ularning retseptlarini bir martalik so'rov bilan olish
        items = order.items.select_related('product').prefetch_related('product__recipes__ingredient')

        for item in items:
            for recipe in item.product.recipes.all():
                deduct_amount = Decimal(recipe.quantity) * Decimal(item.quantity)
                # Atomik tarzda ombor qoldig'ini kamaytirish
                Ingredient.objects.filter(id=recipe.ingredient_id).update(
                    stock=F('stock') - deduct_amount
                )

        order.is_stock_deducted = True

    order.status = OrderStatus.COMPLETED
    if cashier_user and not order.accepted_by:
        order.accepted_by = cashier_user

    order.save(update_fields=['status', 'accepted_by', 'is_stock_deducted', 'updated_at'])
    return order


def order_cancel(*, order: Order, reason: str = "", user=None) -> Order:
    """
    Buyurtmani bekor qilish (Status: CANCELLED).
    Topshirilgan buyurtmani bekor qilib bo'lmaydi.
    """
    if order.status == OrderStatus.COMPLETED:
        raise ValidationError({"detail": "Topshirib bo'lingan buyurtmani bekor qilish mumkin emas."})

    order.status = OrderStatus.CANCELLED
    order.cancellation_reason = reason
    order.save(update_fields=['status', 'cancellation_reason', 'updated_at'])
    return order

