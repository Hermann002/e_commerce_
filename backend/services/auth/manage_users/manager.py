# auth_service/manager.py
import uuid
import logging
from datetime import timedelta
from typing import Optional, Dict, Any

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import User, Tenant, Role, UserRole, Plan, Subscription
from .services import IUserRoleService, UserRoleServiceImpl

logger = logging.getLogger(__name__)

class UserManager:
    """
    Service métier pour gérer la création et le management des utilisateurs.
    Centralise toute la logique métier liée à l'inscription, aux rôles, aux boutiques.
    """

    def __init__(self, role_service: IUserRoleService = None):
        self.role_service = role_service or UserRoleServiceImpl()

    @transaction.atomic
    def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        is_shop_owner: bool = False,
        shop_name: Optional[str] = None,
        shop_slug: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inscrit un utilisateur. Peut créer une boutique si is_shop_owner=True.

        :param email: Email de l'utilisateur
        :param password: Mot de passe
        :param first_name: Prénom
        :param last_name: Nom
        :param is_shop_owner: Si True, crée une boutique
        :param shop_name: Nom de la boutique (obligatoire si is_shop_owner)
        :param shop_slug: Sous-domaine (ex: ma-boutique)
        :return: Dictionnaire avec user, tenant (optionnel), roles
        """
        try:
            # 1. Valider les entrées
            if not email or not password or not first_name or not last_name:
                raise ValidationError("Champs requis manquants.")

            if is_shop_owner and (not shop_name or not shop_slug):
                raise ValidationError("Nom et slug de boutique requis pour shop_owner.")

            if is_shop_owner and Tenant.objects.filter(slug=shop_slug).exists():
                raise ValidationError(f"Le sous-domaine '{shop_slug}' est déjà pris.")

            # 2. Créer l'utilisateur
            user = User.objects.create_user(
                user_id=uuid.uuid4(),
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_verified=False  # À activer plus tard
            )
            logger.info(f"Utilisateur créé : {user.email}")

            # 3. Attribuer rôle de base
            if not self.role_service.assign_role(user.user_id, "customer"):
                raise Exception("Échec attribution rôle 'customer'")

            result = {
                "user": user,
                "tenant": None,
                "roles": self.role_service.get_user_roles(str(user.user_id))
            }

            # 4. Si shop_owner, créer boutique + abonnement + rôle
            if is_shop_owner:
                tenant = self._create_tenant_for_owner(user, shop_name, shop_slug)
                result["tenant"] = tenant

                # Mettre à jour les rôles
                result["roles"] = self.role_service.get_user_roles(str(user.user_id))

            return result

        except Exception as e:
            logger.error(f"Erreur lors de l'inscription : {e}")
            raise ValidationError(f"Échec de l'inscription : {str(e)}")

    @transaction.atomic
    def _create_tenant_for_owner(self, user: User, name: str, slug: str) -> Tenant:
        """
        Crée une boutique pour un propriétaire.
        Attribue le rôle shop_owner, crée un abonnement gratuit.
        """
        # Créer le tenant
        tenant = Tenant.objects.create(
            tenant_id=uuid.uuid4(),
            name=name,
            slug=slug,
            owner=user
        )
        logger.info(f"Boutique créée : {tenant.name} ({tenant.slug})")

        # Attribuer rôle shop_owner
        if not self.role_service.assign_role(
            user_id=str(user.user_id),
            role_name="shop_owner",
            tenant_id=str(tenant.tenant_id),
            assigned_by_id=str(user.user_id)  # auto-attribution
        ):
            raise Exception("Impossible d'attribuer le rôle shop_owner")

        # Associer un plan gratuit
        try:
            free_plan = Plan.objects.get(name="Free")
        except Plan.DoesNotExist:
            free_plan = Plan.objects.create(
                name="Free",
                price=0,
                duration_days=365,
                max_products=50,
                features=["basic_catalog", "5gb_storage"]
            )

        Subscription.objects.create(
            tenant=tenant,
            plan=free_plan,
            status="Active"
        )
        logger.info(f"Abonnement gratuit attribué à {tenant}")

        return tenant

    def promote_to_shop_owner(
        self,
        user_id: str,
        shop_name: str,
        shop_slug: str
    ) -> Tenant:
        """
        Permet à un utilisateur existant de créer une boutique.
        """
        try:
            user = User.objects.get(user_id=user_id)
            return self._create_tenant_for_owner(user, shop_name, shop_slug)
        except User.DoesNotExist:
            raise ValidationError("Utilisateur introuvable.")
        except Exception as e:
            logger.error(f"Échec promotion en shop_owner : {e}")
            raise

    def deactivate_user(self, user_id: str):
        """
        Désactive un utilisateur (soft delete logique)
        """
        try:
            user = User.objects.get(user_id=user_id)
            user.is_active = False
            user.save()
            logger.info(f"Utilisateur désactivé : {user_id}")
        except User.DoesNotExist:
            pass

    def change_password(self, user_id: str, new_password: str):
        """
        Change le mot de passe d'un utilisateur
        """
        try:
            user = User.objects.get(user_id=user_id)
            user.set_password(new_password)
            user.save()
            logger.info(f"Mot de passe changé pour : {user_id}")
        except User.DoesNotExist:
            raise ValidationError("Utilisateur introuvable.")