from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from apps.core.admin import AdminModelPermissionMixin

from .forms import CustomUserCreationForm
from .models import CustomUser

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(AdminModelPermissionMixin, UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ("username", "email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    'status',
                    "is_active",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "first_name", "last_name", "status", "password1", "password2"),
            },
        ),
    )
    permissions = {
        CustomUser.Status.MANAGER: '__all__',
    }

admin.site.unregister(Group)
