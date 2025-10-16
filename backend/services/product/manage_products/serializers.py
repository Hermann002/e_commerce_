from .models import Product, Category, Cart, CartItem, Order, OrderItem, Payment
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.UUIDField(source='parent.category_id', read_only=True, allow_null=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)

    class Meta:
        model = Category
        fields = [
            'category_id',
            'name',
            'slug',
            'parent_id',
            'parent_name',
            'description',
            'created_at'
        ]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'product_id',
            'name',
            'description',
            'price',
            'stock',
            'image_url',
            'is_published',
            'category',
            'category_name',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'category': {'write_only': True},
            'price': {'min_value': 0},
            'stock': {'min_value': 0}
        }

    
class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'product_id',
            'quantity',
            'price',
            'total_price'
        ]

    def get_total_price(self, obj):
        return obj.total_price()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'cart_id',
            'items',
            'total_items',
            'total_amount',
            'created_at',
            'updated_at'
        ]

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_amount(self, obj):
        return sum(item.total_price() for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'product_id',
            'product_name',
            'quantity',
            'price',
            'total_price'
        ]

    def get_total_price(self, obj):
        return obj.total_price()

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.JSONField()

    class Meta:
        model = Order
        fields = [
            'order_id',
            'status',
            'total_amount',
            'shipping_address',
            'payment_method',
            'items',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['order_id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        cart = validated_data['cart']


        order = Order.objects.create(**validated_data)
        return order

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'payment_id',
            'order_id',
            'amount',
            'provider',
            'transaction_id',
            'status',
            'created_at'
        ]
        read_only_fields = ['payment_id', 'created_at']
