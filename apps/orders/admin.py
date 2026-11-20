from django.contrib import admin
from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ['product']
    readonly_fields = ('total_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'customer',
        'status',
        'order_type',
        'payment_type',
        'total_price',
        'accepted_by',
        'is_stock_deducted',
        'created_at',
    )
    list_filter = ('status', 'order_type', 'payment_type', 'is_stock_deducted', 'created_at')
    search_fields = (
        'order_number',
        'customer__username',
        'customer__first_name',
        'customer__last_name',
        'customer__phone',
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('order_number', 'total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
