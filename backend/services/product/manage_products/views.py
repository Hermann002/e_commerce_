from rest_framework import generics, viewsets, filters
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Payment
from .serializers import ProductSerializer, CategorySerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    Provides CRUD operations with custom filtering and permissions.
    """
    serializer_class = ProductSerializer
    
    # Search and ordering configuration
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at']
    ordering = ['name']

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
        ]
    )
    def get_queryset(self):
        """
        Get the list of products with optional filtering.
        """
        queryset = Product.objects.select_related('category')
        
        # Apply filters from query parameters
        category_id = self.request.query_params.get('category')
        is_published = self.request.query_params.get('is_published')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        if is_published:
            is_published_bool = is_published.lower() in ['true', '1']
            queryset = queryset.filter(is_published=is_published_bool)
            
        return queryset

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