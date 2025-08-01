from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomUser(AbstractUser):
    class Status(models.TextChoices):
        MANAGER = 'manager', _('Manager')
        OPERATOR = 'operator', _('Operator')

    is_staff = models.BooleanField(
        _("staff status"),
        help_text=_("Designates whether the user can log into this admin site."),
        default=True,
        editable=False,
    )
    status = models.CharField(choices=Status.choices, max_length=20)
