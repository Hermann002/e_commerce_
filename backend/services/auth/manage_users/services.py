from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from .models import User, Role, UserRole, Tenant
from django.core.exceptions import ObjectDoesNotExist

class IUserRoleService(ABC):
    """
    Interface for user role management services in multitenancy environments.
    """

    @abstractmethod
    def get_user_roles(self, user_id:str) -> List[Dict]:
        """renvoie tous les rôles d'un utilisateur (globaux + par tenant)

        Args:
            user_id (str): _description_

        Returns:
            List[Dict]: _description_
        """

        pass

    @abstractmethod
    def has_role(self, user_id, role_name:str, tenant_id: Optional[str] = None) -> bool:
        """Vérifie si un utilisateur a un rôle donné (global ou spécifique à un tenant)
        
        Args:
            user_id (_type_): _description_
            role_name (str): _description_
            tenant_id (Optional[str], optional): _description_. Defaults to None.

        Returns:
            bool: _description_
        """

        pass

    @abstractmethod
    def get_user_tenants(self, user_id:str) -> List[Dict]:
        """Renvoie les tenants auxquels l'utilisateur a accès, avec un rôle dans chacun

        Args:
            user_id (str): _description_

        Returns:
            List[Dict]: _description_
        """

        pass

    @abstractmethod
    def assign_role(self, user_id:str, role_name:str, tenant_id:Optional[str] = None):
        """Attribue un rôle à l'utilisateur

        Args:
            user_id (str): _description_
            role_name (str): _description_
            tenant_id (Optional[str], optional): _description_. Defaults to None.
        """
        pass

    @abstractmethod
    def remove_role(self, user_id: str, role_name: str, tenant_id: Optional[str] = None) -> bool:
        """
        Retire un rôle à un utilisateur
        """
        pass

class UserRoleServiceImpl(IUserRoleService):
    def get_user_roles(self, user_id:str)->List[Dict]:
        try:
            user_roles = UserRole.objects.filter(User__user_id=user_id).select_related('role', 'tenant')
            return [
                {
                    "role": ur.role.name,
                    "scope": "global" if ur.tenant is None else "tenant",
                    "tenant_id": str(ur.tenant.tenant_id) if ur.tenant else None,
                    "assigned_at": ur.assigned_at.isoformat()
                }
                for ur in user_roles
            ]
        except Exception:
            return []
    
    def has_role(self, user_id:str, role_name:str, tenant_id:Optional[str] = None)->bool:
        filters = {"User__user_id": user_id, "role__name": role_name}
        if tenant_id:
            filters["tenant__tenant_id"] = tenant_id
        else:
            filters["tenant__isnull"] = True
        return UserRole.objects.filter(**filters).exists()

    def get_user_tenants(self, user_id:str)->List[Dict]:
        try:
            user_roles = UserRole.objects.filter(User__user_id=user_id).select_related('tenant', 'role')
            return [
                {
                    "tenant_id": str(ur.tenant.tenant_id),
                    "tenant_name": ur.tenant.name,
                    "role": ur.role.name,
                    "access_level": "owner" if ur.role.name == "shop_owner" else "employee"
                }
                for ur in user_roles if ur.tenant
            ]
        except Exception:
            return []
        
    def assign_role(self, user_id:str, role_name:str, tenant_id:Optional[str] = None, assigned_by_id:str = None)->bool:
        try:
            user = User.objects.get(user_id=user_id)
            role = Role.objects.get(name=role_name)
            assigned_by = User.objects.get(user_id=assigned_by_id) if assigned_by_id else None
            tenant = Tenant.objects.get(tenant_id=tenant_id) if tenant_id else None

            UserRole.objects.get_or_create(
                user=user,
                role=role,
                tenant=tenant,
                defaults={'assigned_by': assigned_by}
            )
            return True
        except (User.DoesNotExist, Role.DoesNotExist, Tenant.DoesNotExist):
            return False

    def remove_role(self, user_id: str, role_name: str, tenant_id: Optional[str] = None) -> bool:
        try:
            filters = {"user__user_id": user_id, "role__name": role_name}
            if tenant_id:
                filters["tenant__tenant_id"] = tenant_id
            else:
                filters["tenant__isnull"] = True
            deleted, _ = UserRole.objects.filter(**filters).delete()
            return deleted > 0
        except Exception:
            return False