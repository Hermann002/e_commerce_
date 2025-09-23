from django.db import models
from django.contrib.auth.models import User
from .enums import OrderStatus, PaymentMethod, PaymentStatus

import uuid


class LocalTenant(models.Model):
    tenant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Nom de la boutique")
    owner_id = models.UUIDField(help_text="ID du propriétaire (copié depuis auth-service)")
    is_active = models.BooleanField(default=True, help_text="Actif ou désactivé")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.tenant_id}] {self.name}"

    class Meta:
        db_table = 'local_tenant'
        verbose_name = "Local Tenant"
        verbose_name_plural = "Local Tenants"

class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    tenant = models.ForeignKey(LocalTenant, on_delete=models.CASCADE, related_name='categories')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk}-{self.name}"
    
    class Meta:
        db_table = 'category'
        unique_together = ('slug', 'tenant')

class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tenant = models.ForeignKey(LocalTenant, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image_url = models.CharField(max_length=255)
    is_published = models.BooleanField()
    stock = models.PositiveIntegerField(default=0)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk}-{self.name}"
    
    class Meta:
        db_table = 'product'
        indexes = [
            models.Index(fields=['tenant', 'is_published']),
            models.Index(fields=['category']),
        ]
    
    
class Cart(models.Model):
    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.UUIDField(null=True, blank=True, help_text="Null si anonyme")
    tenant = models.ForeignKey(LocalTenant, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True, help_text="Pour les utilisateurs anonymes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.pk} for User {self.user}"
    
    class Meta:
        db_table = 'cart'
        unique_together = ('user', 'tenant')
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='product_id')  # Explicitly reference the UUID field
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x Product {self.product}"

    class Meta:
        db_table = 'cart_item'
        unique_together = ('cart', 'product')

class Order(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.UUIDField(null=True, blank=True, help_text="Null si anonyme")
    tenant = models.ForeignKey(LocalTenant, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    billing_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.pk} for User {self.user} - Status: {self.status}"

    class Meta:
        db_table = 'order'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status']),
        ]
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of order
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in Order {self.order.pk}"
    
class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    provider = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.pk} for Order {self.order.pk} - Status: {self.status}"
    
    class Meta:
        db_table = 'payment'