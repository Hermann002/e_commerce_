# auth_service/manager.py
import uuid
import logging
from datetime import timedelta
from typing import Optional, Dict, Any, TypedDict
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import transaction

from .services import IUserRoleService, UserRoleServiceImpl

from django.utils.translation import gettext as _
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)

class UserData(TypedDict):
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool

def get_user_by_id(user_id: str) -> Optional[UserData]:
    """Interface pour récupérer un utilisateur"""
    User = apps.get_model('manage_users', 'User')
    try:
        user = User.objects.get(id=user_id)
        return UserData(
            user_id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified
        )
    except User.DoesNotExist:
        return None

def create_user_record(user_data: Dict[str, Any]) -> UserData:
    """Interface pour créer un utilisateur"""
    User = apps.get_model('manage_users', 'User')
    user = User.objects.create_user(**user_data)
    print("user create")
    return UserData(
        user_id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_verified=user.is_verified
    )

def get_or_create_free_plan():
    """Interface pour obtenir ou créer le plan gratuit"""
    Plan = apps.get_model('manage_users', 'Plan')
    try:
        plan = Plan.objects.get(name="Free")
    except Plan.DoesNotExist:
        plan = Plan.objects.create(
            name="Free",
            price=0,
            duration_days=365,
            max_products=50,
            features=["basic_catalog", "5gb_storage"]
        )
    return plan

def create_subscription(plan_id: str):
    """Interface pour créer un abonnement"""
    Subscription = apps.get_model('manage_users', 'Subscription')
    Plan = apps.get_model('manage_users', 'Plan')
    plan = Plan.objects.get(id=plan_id)

    return Subscription.objects.create(
        plan=plan,
        status="Active"
    )

class UserManager:
    """
    Service métier pour gérer la création et le management des utilisateurs.
    Centralise toute la logique métier liée à l'inscription, aux rôles, aux boutiques.
    """

    def __init__(self, role_service: IUserRoleService = None):
        self.role_service = role_service or UserRoleServiceImpl()
    
    def create_user(self, email, first_name, last_name, password, **kwargs):
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("an email address is required"))
        
        if not first_name:
            raise ValueError(_("first name is required"))
        
        if not last_name:
            raise ValueError(_("last name is required"))
        
        user = self.model(email=email, first_name=first_name, last_name=last_name, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    @transaction.atomic
    def register_user(
            self,
            email: str,
            password: str,
            first_name: str,
            last_name: str
        ) -> Dict[str, Any]:
        """
        Inscrit un utilisateur sans créer de boutique.

        :return: Dictionnaire contenant l'utilisateur et ses rôles
        """
        try:
            # Validation
            if not all([email, password, first_name, last_name]):
                raise ValidationError("Les champs email, mot de passe, prénom et nom sont obligatoires.")

            # Créer l'utilisateur via le service métier
            user_data = {
                'id': uuid.uuid4(),
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'is_verified': False
            }
            print(user_data)
            try:
                user = create_user_record(user_data)
                logger.info(f"Utilisateur inscrit : {user['email']}")
            except Exception as e: 
                logger.error(f"Erreur création utilisateur : {e}")
                raise ValidationError(f"Erreur lors de la création de l'utilisateur : {e}")

            # Attribuer le rôle de base
            if not self.role_service.assign_role(str(user['user_id']), "customer"):
                raise Exception("Échec d'attribution du rôle 'customer'")

            return {
                "user": user,
                "roles": self.role_service.get_user_roles(str(user['user_id']))
            }

        except Exception as e:
            logger.error(f"Erreur lors de l'inscription : {e}")
            raise ValidationError(f"Échec de l'inscription : {str(e)}")
        
    def deactivate_user(self, user_id: str):
        user = get_user_by_id(user_id)
        if user:
            user['is_active'] = False
            create_user_record(user)
            logger.info(f"Utilisateur désactivé : {user_id}")

    def authenticate(self, email: str, password: str) -> Optional[UserData]:
        User = apps.get_model('manage_users', 'User')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Erreur d'authentification : {e}")
            return None