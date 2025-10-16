# product_service/utils/jwt.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request
from rest_framework.exceptions import AuthenticationFailed

def get_validated_token_from_request(request: Request):
    """
    Extrait et valide le JWT depuis la requête, en utilisant SimpleJWT.
    Retourne le token validé ou None si absent.
    """
    jwt_auth = JWTAuthentication()
    
    header = jwt_auth.get_header(request)
    if header is None:
        return None

    raw_token = jwt_auth.get_raw_token(header)
    if raw_token is None:
        return None

    validated_token = jwt_auth.get_validated_token(raw_token)
    return validated_token