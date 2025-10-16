from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext as _

class BaseUserManager(BaseUserManager):
    def normalize_email(self, email):
        return super().normalize_email(email)

    def email_validator(self, email):
        if not email:
            raise ValueError(_("Email cannot be empty"))
        return True

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
    
    def create_superuser(self, email, first_name, last_name, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if kwargs.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, first_name, last_name, password, **kwargs)