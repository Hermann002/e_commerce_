from django.db import models

class PlanChoice(models.TextChoices):
    FREE = 'FREE', 'Free'
    BASIC = 'BASIC', 'Basic'
    PREMIUM = 'PREMIUM', 'Premium'
    ENTERPRISE = 'ENTERPRISE', 'Enterprise'

class StatusChoice(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    SUSPENDED = 'SUSPENDED', 'Suspended'
    CANCELLED = 'CANCELLED', 'Cancelled'