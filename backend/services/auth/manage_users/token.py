from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import UserRole

class TenantAwareAccessTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        user_roles = UserRole.objects.filter(user=user).select_related('tenant', 'role')
        tenants_data = []
        global_roles = []
        
        print("hello tenants")
        for ur in user_roles:
            if ur.tenant:
                print("tenant found")
                tenants_data.append({
                    "tenant_id": str(ur.tenant.tenant_id),
                    "tenant_name": ur.tenant.name,
                    "role": ur.role.name
                })
            else:
                print("global role found")
                global_roles.append(ur.role.name)
        
        token['tenants'] = tenants_data
        token['global_roles'] = global_roles

        return token