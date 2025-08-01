from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CrmSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crm_system'
    verbose_name = _('CRM Management System')
