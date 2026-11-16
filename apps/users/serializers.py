from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.users.models import User, UserRole
from apps.users.services import cashier_create, cashier_update


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login qilinganda access va refresh tokenlar bilan birga
    foydalanuvchining id va role maydonlarini ham qaytaruvchi serializer.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = self.user.id
        data['role'] = self.user.role
        return data


class CashierSerializer(serializers.ModelSerializer):
    """
    Kassir ma'lumotlarini o'qish uchun serializer.
    """
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'phone',
            'role',
            'is_active',
            'date_joined',
        ]
        read_only_fields = fields


class CashierCreateSerializer(serializers.Serializer):
    """
    Yangi kassir yaratish uchun serializer (faqat Admin foydalanadi).
    """
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=4)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    phone = PhoneNumberField(required=False, allow_null=True)

    def create(self, validated_data):
        return cashier_create(**validated_data)

    def to_representation(self, instance):
        return CashierSerializer(instance).data


class CashierUpdateSerializer(serializers.Serializer):
    """
    Kassir ma'lumotlarini yangilash uchun serializer.
    Rol maydoni kiritilmaydi, o'zgartirish taqiqlanadi.
    """
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone = PhoneNumberField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=4)

    def update(self, instance, validated_data):
        return cashier_update(instance, **validated_data)

    def to_representation(self, instance):
        return CashierSerializer(instance).data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Shaxsiy profil ma'lumotlarini ko'rish va tahrirlash (/me/ endpointi).
    Foydalanuvchi o'z rolini aslo o'zgartira olmaydi.
    """
    password = serializers.CharField(write_only=True, required=False, min_length=4)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'phone',
            'role',
            'password',
            'date_joined',
        ]
        read_only_fields = ['id', 'username', 'role', 'date_joined']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            try:
                validate_password(password, user=instance)
            except DjangoValidationError as err:
                raise serializers.ValidationError({"password": list(err.messages)})
            instance.set_password(password)

        instance.save()
        return instance

