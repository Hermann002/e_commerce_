# models/user.py
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from datetime import timedelta

from .enums import PlanChoice, StatusChoice

from .manager import UserManager

class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)  # utilisé pour login
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'user'

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Ex: admin, customer, shop_owner")
    description = models.TextField(blank=True, null=True)
    permissions = models.JSONField(default=dict, help_text="Permissions sous forme {action: true/false}")
    is_global = models.BooleanField(default=True, help_text="S'applique à tout le système")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'role'

class UserRole(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='assigned_roles')

    class Meta:
        db_table = 'user_role'
        unique_together = ('user', 'role', 'tenant')  # Pas de doublon
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['tenant']),
        ]

    def __str__(self):
        if self.tenant:
            return f"{self.user} - {self.role} ({self.tenant})"
        return f"{self.user} - {self.role} (global)"

class Tenant(models.Model):
    tenant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, help_text="Sous-domaine : maboutique.nextgen.shop")
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='owned_tenants')
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.slug})"

    class Meta:
        db_table = 'tenant'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
        ]

class Plan(models.Model):
    name = models.CharField(max_length=50, choices=PlanChoice.choices, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duration_days = models.PositiveIntegerField(default=30)
    max_products = models.PositiveIntegerField()
    features = models.JSONField(default=list, help_text=["analytics", "custom_domain", ...])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_name_display()} ({self.price}€)"

    class Meta:
        db_table = 'plan'

class Subscription(models.Model):
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.ACTIVE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tenant} - {self.plan}"

    class Meta:
        db_table = 'subscription'
        indexes = [
            models.Index(fields=['tenant', 'status']),
        ]

