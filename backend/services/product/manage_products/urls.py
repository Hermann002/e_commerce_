from django.urls import path, include
from .views import CategoryViewSet, ProductViewSet, CartViewSet, PaymentViewSet, OrderViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', CartViewSet.as_view({'get': 'list'}), name='cart-list'),
    path('cart/add/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add'),
    path('cart/<uuid:cart_id>/remove/', CartViewSet.as_view({'delete': 'remove_item'}), name='cart-remove'),
    # API Schema
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ReDoc
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]