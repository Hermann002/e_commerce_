# # product_service/middleware.py
# from django.http import HttpResponseForbidden, HttpResponseNotFound
# from django.utils.deprecation import MiddlewareMixin
# import re
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from .utils import get_validated_token_from_request

# class TenantAccessMiddleware(MiddlewareMixin):
#     """
#     Middleware qui :
#     1. Résout le tenant via le sous-domaine
#     2. Valide le JWT en s'appuyant sur rest_framework_simplejwt
#     3. Vérifie que l'utilisateur a accès au tenant demandé
#     4. Expose request.tenant et request.user_tenant_role
#     """

#     EXEMPT_PATHS = [
#         '/api/schema/', '/api/redoc/', '/api/docs/', '/health/', '/admin/'
#     ]

#     def process_request(self, request):
#         print("second")
#         # 1. Ignorer certaines routes
#         """les routes commencent par /api/schema/, /api/redoc/, /api/docs/, /health/ ou /admin/ sont exemptées"""
#         if any(re.match(f'^{path}', request.path) for path in self.EXEMPT_PATHS):
#             return None
#         # if request.path in self.EXEMPT_PATHS:
#         #     return None

#         # 2. Extraire le slug du sous-domaine
#         host = request.get_host().split(':')[0]

#         print("fourth")
#         slug = request.headers.get('X-Tenant-Slug')
#         if not slug:
#             request.tenant = None
#             request.user_tenant_role = None
#         print(slug)

#         # 3. Trouver le tenant local
#         try:
#             local_tenant = LocalTenant.objects.get(slug=slug, is_active=True)
#             request.tenant = local_tenant
#         except LocalTenant.DoesNotExist:
#             return HttpResponseNotFound("Boutique introuvable ou inactive.")
#         # 4. Extraire et valider le JWT

#         try:
#             validated_token = get_validated_token_from_request(request)
#             if validated_token is None:
#                 return HttpResponseForbidden("Token manquant")
#         except AuthenticationFailed as e:
#             return HttpResponseForbidden(f"Authentification échouée : {str(e)}")

#         # 5. Vérifier que le tenant fait partie des tenants autorisés
#         user_tenants = validated_token.get('tenants', [])
#         user_tenant_ids = [t['tenant_id'] for t in user_tenants]
#         print(user_tenants)
#         print(local_tenant.tenant_id)

#         if str(local_tenant.tenant_id) not in user_tenant_ids:
#             return HttpResponseForbidden(
#                 f"Accès refusé à la boutique '{local_tenant.name}'. "
#                 "Vous n'avez pas les permissions nécessaires."
#             )

#         # 6. Ajouter les infos utiles à la requête
#         request.jwt_token = validated_token
#         request.user_tenant_role = next(
#             (t['role'] for t in user_tenants if t['tenant_id'] == str(local_tenant.tenant_id)),
#             None
#         )
#         request.user_is_authenticated = True

#         return None  # Continue vers la vue