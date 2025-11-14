import os

from flask import Flask, request
from .config import Config
from .middleware.auth import verify_jwt

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'gateway.sqlite'),
    )
    app.config.from_object(Config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import app as app_module
    app.register_blueprint(app_module.bp)

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'
    
    # Liste des routes protégées
    PROTECTED_ROUTES = [
        '/api/products',
    ]
    UNPROTECTED_ROUTES = [
        '/api/products/products', '/api/products/categories',
    ]

    SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

    @app.before_request
    def before_request():
        # Appliquer auth uniquement sur les routes sensibles
        if any(request.path.startswith(prefix) for prefix in UNPROTECTED_ROUTES) and request.method in SAFE_METHODS:
            return None
        if any(request.path.startswith(prefix) for prefix in PROTECTED_ROUTES):
            error_response = verify_jwt(required=True)
            if error_response:
                return error_response

    return app