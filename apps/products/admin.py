from django.contrib import admin
from apps.products.models import Category, Product, ProductRecipe


class ProductRecipeInline(admin.TabularInline):
    model = ProductRecipe
    extra = 1
    autocomplete_fields = ['ingredient']
    verbose_name = 'Retsept tarkibi'
    verbose_name_plural = 'Retsept tarkiblari (Xomashyolar)'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('order', 'name')
    list_editable = ('order', 'is_active')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'is_active', 'recipes_count', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    list_editable = ('price', 'is_active')
    inlines = [ProductRecipeInline]

    @admin.display(description='Tarkiblar soni')
    def recipes_count(self, obj):
        return obj.recipes.count()


@admin.register(ProductRecipe)
class ProductRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'ingredient', 'quantity')
    list_filter = ('product__category', 'ingredient')
    search_fields = ('product__name', 'ingredient__name')
    autocomplete_fields = ['product', 'ingredient']
