from .models import LocalTenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_id = request.headers.get('X-Tenant-ID')
        if tenant_id:
            try:
                request.tenant = LocalTenant.objects.get(tenant_id=tenant_id, is_active=True)
            except LocalTenant.DoesNotExist:
                request.tenant = None
        else:
            request.tenant = None
        return self.get_response(request)