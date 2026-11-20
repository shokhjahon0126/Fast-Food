from django.contrib import admin
from apps.inventory.models import Ingredient, Supply


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'unit',
        'stock',
        'min_stock',
        'is_active',
        'updated_at',
    )
    list_filter = ('unit', 'is_active')
    search_fields = ('name',)
    ordering = ('name',)
    list_editable = ('min_stock', 'is_active')


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ingredient',
        'quantity',
        'cost_price',
        'total_price',
        'supplier',
        'created_by',
        'created_at',
    )
    list_filter = ('ingredient', 'created_at')
    search_fields = ('ingredient__name', 'supplier', 'notes')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('total_price', 'created_at')

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
