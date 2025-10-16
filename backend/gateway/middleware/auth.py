# gateway/middleware/auth.py
import jwt
import requests
from flask import g, jsonify, request
from ..config import Config

def verify_jwt(required=False):
    token = request.headers.get('Authorization')
    if not token:
        if required:
            return jsonify({"error": "Token manquant"}), 401
        g.user = None
        return None

    if token.startswith("Bearer "):
        token = token[7:]

    try:
        # Utilise la clé publique pour vérifier
        payload = jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=['HS256']  # ou ['RS256'] si tu utilises RSA
        )
        g.user = payload
        g.authenticated = True
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expiré"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token invalide"}), 401

    return None