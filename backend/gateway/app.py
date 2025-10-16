# gateway/app.py
from flask import Flask, request, Response, g, jsonify, Blueprint
import requests
from urllib.parse import urljoin
from .config import Config


bp = Blueprint('app', __name__, url_prefix='/')


def proxy_request(service_url: str, path: str):
    target_url = urljoin(f"{service_url}/", path)
    
    # Copie la requête
    method = request.method
    data = request.get_data()
    headers = {key: value for key, value in request.headers if key != 'Host'}

    try:
        resp = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=data,
            params=request.args,
            stream=True
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)

    except requests.ConnectionError as e:
        return jsonify({"error": f"Service indisponible: {e}"}), 502


# @bp.before_request
# def before_request():
#     # Appliquer auth uniquement sur les routes sensibles
#     if any(request.path.startswith(prefix) for prefix in PROTECTED_ROUTES):
#         error_response = verify_jwt(required=True)
#         if error_response:
#             return error_response


@bp.route('/api/auth/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def auth_proxy(path):
    return proxy_request(Config.AUTH_SERVICE, f"/api/auth/{path}")

@bp.route('/api/products/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def product_proxy(path):
    return proxy_request(Config.PRODUCT_SERVICE, f"/api/products/{path}")

@bp.route('/api/notifications/<path:path>', methods=['GET', 'POST'])
def notification_proxy(path):
    return proxy_request(Config.NOTIFICATION_SERVICE, f"/api/notifications/{path}")


# Route santé
@bp.route('/health')
def health():
    return jsonify({"status": "ok", "service": "gateway"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)