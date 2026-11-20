from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'phone',
        'role',
        'is_staff',
        'is_active',
    )
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'phone')
    ordering = ('-id',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo‘shimcha ma’lumotlar', {'fields': ('phone', 'role')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Qo‘shimcha ma’lumotlar', {'fields': ('phone', 'role')}),
    )
