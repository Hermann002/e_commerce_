from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

class IUserRoleService(ABC):
    """
    Interface for user role management services in multitenancy environments.
    """

    @abstractmethod
    def get_user_roles(self, user_id:str) -> List[Dict]:
        """renvoie tous les rôles d'un utilisateur

        Args:
            user_id (str): _description_

        Returns:
            List[Dict]: _description_
        """

        pass




class UserRoleServiceImpl(IUserRoleService):
    def __init__(self):
        self.User = apps.get_model('manage_users', 'User')
        self.Role = apps.get_model('manage_users', 'Role')
        self.UserRole = apps.get_model('manage_users', 'UserRole')

    def get_user_roles(self, user_id:str)->List[Dict]:
        try:
            user_roles = self.UserRole.objects.filter(user__id=user_id).select_related('role')
            return [
                {
                    "role": ur.role.name,
                    "assigned_at": ur.assigned_at.isoformat()
                }
                for ur in user_roles
            ]
        except Exception:
            return []
    
    def has_role(self, user_id:str, role_name:str,)->bool:
        filters = {"User__id": user_id, "role__name": role_name}
        return self.UserRole.objects.filter(**filters).exists()

    def assign_role(self, user_id:str, role_name:str)->bool:
        try:
            user = self.User.objects.get(id=user_id)
            role = self.Role.objects.get(name=role_name)
            self.UserRole.objects.create(user=user, role=role)
            return True
        except ObjectDoesNotExist:
            return False
        except Exception:
            return False