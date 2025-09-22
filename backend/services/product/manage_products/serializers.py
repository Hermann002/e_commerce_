from .models import Product, Category, Cart, CartItem, Order, OrderItem, Payment, LocalTenant
from rest_framework import serializers

class LocalTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalTenant
        fields = [
            'tenant_id',
            'name',
            'owner_id',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['tenant_id', 'owner_id', 'created_at', 'updated_at']

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
            'category_id',
            'category_name',
            'created_at',
            'updated_at'
        ]
        extra_kwargs = {
            'category_id': {'write_only': True},
            'price': {'min_value': 0},
            'stock': {'min_value': 0}
        }

    def validate(self, data):
        tenant = self.context['request'].tenant
        if data.get('category') and data['category'].tenant != tenant:
            raise serializers.ValidationError("La catégorie n'appartient pas à ce tenant.")
        return data
    
class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'product_id',
            'quantity',
            'unit_price',
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

    class Meta:
        model = OrderItem
        fields = [
            'product_id',
            'product_name',
            'quantity',
            'unit_price',
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

        # Vérifier que le panier appartient bien au tenant
        if cart.tenant != request.tenant:
            raise serializers.ValidationError("Le panier n'appartient pas à ce tenant.")

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

    def validate(self, data):
        order = data['order']
        if order.tenant != self.context['request'].tenant:
            raise serializers.ValidationError("Commande non accessible dans ce contexte.")
        return data