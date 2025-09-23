from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Role, UserRole, Tenant

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'is_verified',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['user_id', 'is_verified', 'created_at', 'updated_at']