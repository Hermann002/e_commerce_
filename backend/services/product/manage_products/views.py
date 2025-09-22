from rest_framework import generics, viewsets, filters, status
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Payment, LocalTenant
from .serializers import LocalTenantSerializer, ProductSerializer, CategorySerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action


from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


class LocalTenantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LocalTenant.objects.all()
    serializer_class = LocalTenantSerializer

@extend_schema(tags=['Categories'])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tenant']
    lookup_field = 'category_id'

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    Provides CRUD operations with custom filtering and permissions.
    """
    serializer_class = ProductSerializer
    
    # Search and ordering configuration
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'category_id']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at']
    ordering = ['name']
    lookup_field = 'product_id'

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                description='Filter products by category ID'
            ),
            OpenApiParameter(
                name='is_published',
                type=OpenApiTypes.BOOL,
                description='Filter products by published status'
            ),
        ],
        tags=['Products'],
    )
    def get_queryset(self):
        """
        Get the list of products with optional filtering.
        """
        queryset = Product.objects.select_related('category')
        tenant = self.request.tenant
        
        # Apply filters from query parameters
        category_id = self.request.query_params.get('category')
        is_published = self.request.query_params.get('is_published')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        if is_published:
            is_published_bool = is_published.lower() in ['true', '1']
            queryset = queryset.filter(is_published=is_published_bool)
        
        if not tenant:
            return Product.objects.none()
        return queryset.filter(tenant=tenant)

    def get_permissions(self):
        """
        Define permission classes based on the action.
        List and retrieve are public, other actions require authentication.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)


@extend_schema(tags=['Cart'])
class CartViewSet(viewsets.ViewSet):
    lookup_field = 'cart_id'

    def list(self, request):
        """Récupère le panier de l'utilisateur ou de la session"""
        tenant = request.tenant
        user_id = request.user_id  # extrait du JWT
        session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(
            user_id=user_id,
            session_key=session_key,
            tenant=tenant
        )
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        tenant = request.tenant
        user_id = request.user_id
        session_key = request.session.session_key

        cart, _ = Cart.objects.get_or_create(
            user_id=user_id,
            session_key=session_key,
            tenant=tenant
        )

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        # Valider que le produit existe (appel interne ou cache)
        # Ici on suppose qu'on a déjà vérifié via API

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={'quantity': quantity, 'unit_price': 0}  # prix mis à jour plus tard
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_item(self, request, cart_id=None):
        try:
            cart = Cart.objects.get(cart_id=cart_id)
            product_id = request.data.get('product_id')
            cart.items.filter(product_id=product_id).delete()
            return Response(CartSerializer(cart).data)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    lookup_field = 'order_id'

    def get_queryset(self):
        user_id = self.request.user_id
        tenant = self.request.tenant
        return Order.objects.filter(user_id=user_id, tenant=tenant)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user_id, tenant=self.request.tenant)

@extend_schema(tags=['Payments'])
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = 'payment_id'

    def get_queryset(self):
        tenant = self.request.tenant
        return Payment.objects.filter(order__tenant=tenant)