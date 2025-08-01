from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CustomUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.custom_user'
    verbose_name = _('Authentication')
