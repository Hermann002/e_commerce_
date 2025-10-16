from rest_framework import serializers
from django.core.validators import MinLengthValidator
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.openapi import OpenApiTypes
from .models import User

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        validators=[MinLengthValidator(8)]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        validators=[MinLengthValidator(8)]
    )
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']
        required = "__all__"

    def validate(self, data):
        if data['password'] != data.get('confirm_password'):
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

# class UserLoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['email', 'password']
#         required = "__all__"
    
    