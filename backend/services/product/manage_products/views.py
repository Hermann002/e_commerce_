from rest_framework import generics, viewsets
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
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.select_related('category').all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                description='Filter products by category ID',
                examples=[
                    OpenApiExample('Category 1', value=1),
                    OpenApiExample('Category 2', value=2),
                ]
            ),
            OpenApiParameter(
                name='is_published',
                type=OpenApiTypes.BOOL,
                description='Filter products by published status',
                examples=[
                    OpenApiExample('Published', value=True),
                    OpenApiExample('Unpublished', value=False),
                ]
            ),
        ]
    )

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        category_id = request.query_params.get('category')
        is_published = request.query_params.get('is_published')

        queryset = self.get_queryset()
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        if is_published is not None:
            if is_published.lower() in ['true', '1']:
                queryset = queryset.filter(is_published=True)
            elif is_published.lower() in ['false', '0']:
                queryset = queryset.filter(is_published=False)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)