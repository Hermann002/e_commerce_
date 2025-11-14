# product_service/middleware.py
import jwt
from django.http import HttpResponseForbidden
from django.conf import settings
import json

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')

        public_paths = [
            "/api/products/categories/",
        ]
        if any(request.path.startswith(path) for path in public_paths):
            print("true")
            return self.get_response(request)

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                payload = jwt.decode(
                    token,
                    settings.SIMPLE_JWT['SIGNING_KEY'],
                    algorithms=['HS256']
                )
                # Stocke dans request, sans toucher à request.user
                request.jwt_payload = payload
                request.user_id = payload.get('user_id')
                print("Here middle")
            except jwt.ExpiredSignatureError:
                return HttpResponseForbidden("Token expiré !!!")
            except jwt.InvalidTokenError:
                return HttpResponseForbidden("Token invalide")
        else:
            request.jwt_payload = None
            request.user_id = None

        return self.get_response(request)