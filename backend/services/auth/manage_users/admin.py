from django.contrib import admin
from .models import User, Role, UserRole, Plan, Subscription

admin.site.site_header = "User Management Admin"
admin.site.site_title = "User Management Admin Portal"
admin.site.index_title = "Welcome to the User Management Admin Portal"
# Register your models here.
admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(Plan)
admin.site.register(Subscription)