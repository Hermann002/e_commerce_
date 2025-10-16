import os
from decouple import config as env

class Config:
    AUTH_SERVICE = env('AUTH_SERVICE')
    PRODUCT_SERVICE = env('PRODUCT_SERVICE')
    NOTIFICATION_SERVICE = env('NOTIFICATION_SERVICE')
    JWT_SECRET_KEY = env('JWT_SECRET_KEY')

    # Clé publique pour vérifier le JWT
#     JWT_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
# MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
# -----END PUBLIC KEY-----"""

    DEBUG = env('DEBUG', 'False').lower() == 'true'