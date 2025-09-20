from django.contrib import admin

admin.site.site_header = "Product Management Admin"
admin.site.site_title = "Product Management Admin Portal"
admin.site.index_title = "Welcome to the Product Management Admin Portal"

# Register your models here.
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Payment
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)

