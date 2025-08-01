from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

# Create your models here.

class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated'))

    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]


class DescriptiveModel(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class NamedModel(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))

    class Meta:
        abstract = True
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self):
        return self.name


class UniqueNamedModel(NamedModel):
    class Meta(NamedModel.Meta):
        abstract = True
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='unique_name_%(class)s',
                violation_error_message=_('Record with this name already exists'),
            )
        ]
