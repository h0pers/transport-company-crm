from django.conf import settings
from django.db import models
from django.db.models import BooleanField, Case, Count, OuterRef, Q, Subquery, Value, When
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from apps.core.models import DescriptiveModel, TimestampModel, UniqueNamedModel

__all__ = [
    'Canton',
    'LegalSeat',
    'LegalForm',
    'Company',
    'CompanyContactRecord',
    'CompanyNote',
    'CompanyType',
]


# Create your models here.

class Canton(UniqueNamedModel):
    class Meta(UniqueNamedModel.Meta):
        verbose_name = _('Canton')
        verbose_name_plural = _('Canton')


class LegalSeat(UniqueNamedModel):
    class Meta(UniqueNamedModel.Meta):
        verbose_name = _('Legal seat')
        verbose_name_plural = _('Legal seats')


class LegalForm(UniqueNamedModel):
    class Meta(UniqueNamedModel.Meta):
        verbose_name = _('Legal form')
        verbose_name_plural = _('Legal forms')


class CompanyQuerySet(models.QuerySet):
    def annotate_last_contact_status(self):
        last_status_sq = (CompanyContactRecord.objects
                          .filter(company=OuterRef('pk'))
                          .order_by('-contacted_at')
                          .values('status')
                          )[:1]
        return (
            self
            .annotate(last_status=Subquery(last_status_sq))
        )

    def filter_last_contact_status(self, status: str):
        return (
            self
            .annotate_last_contact_status()
            .filter(last_status=status)
        )

    def annotate_contact_ready_status(self):
        query = Q(contact_records_amount=0) & (~Q(phone='') | ~Q(email=''))
        return (
            self
            .annotate(
                contact_records_amount=Count('contact_records'),
                contact_ready=Case(
                    When(
                        condition=query,
                        then=Value(True),
                    ),
                    output_field=BooleanField(),
                    default=Value(False),
                ))
        )

    def filter_contact_ready_status(self, status: bool):
        return (
            self
            .annotate_contact_ready_status()
            .filter(contact_ready=status)
        )


class CompanyManager(BaseManager.from_queryset(CompanyQuerySet)):
    pass


class CompanyType(UniqueNamedModel):
    class Meta(UniqueNamedModel.Meta):
        verbose_name = _('Company type')
        verbose_name_plural = _('Company types')


class Company(DescriptiveModel, TimestampModel):
    in_liquidation = models.BooleanField(default=False, blank=True, verbose_name=_('Liquidation'))
    type = models.ForeignKey(CompanyType, on_delete=models.PROTECT, verbose_name=_('Type'))
    website = models.URLField(blank=True, verbose_name=_('Website'))
    phone = models.CharField(max_length=30, blank=True, verbose_name=_('Phone number'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    legal_seat = models.ForeignKey(
        LegalSeat,
        on_delete=models.PROTECT,
        related_name='companies',
        verbose_name=_('Legal seat')
    )
    legal_form = models.ForeignKey(
        LegalForm,
        on_delete=models.PROTECT,
        related_name='companies',
        verbose_name=_('Legal form')
    )
    canton = models.ForeignKey(
        Canton,
        on_delete=models.PROTECT,
        related_name='companies',
        verbose_name=_('Canton')
    )

    objects = CompanyManager()

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['-created_at']),
        ]


class CompanyNote(TimestampModel):
    note = models.TextField(verbose_name=_('Note'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('User')
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Company')
    )

    class Meta:
        verbose_name = _('Company note')
        verbose_name_plural = _('Company notes')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return _('%(user)s has left comment') % {
            'user': str(self.user)
        }


class CompanyContactRecord(models.Model):
    class Status(models.TextChoices):
        DECLINE = 'decline', _('Decline')
        AGREED = 'agreed', _('Agreed')
        REPEAT = 'repeat', _('Repeat')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('User')
    )
    status = models.CharField(choices=Status.choices, max_length=20)
    contacted_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contact_records')
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['contacted_at']
        indexes = [
            models.Index(fields=['contacted_at'])
        ]
        verbose_name = _('Company contact record')
        verbose_name_plural = _('Company contact records')

    def __str__(self):
        return _('%(user)s contacted at %(contacted_at)s') % {
            'user': str(self.user),
            'contacted_at': self.contacted_at.strftime("%Y-%m-%d %H:%M"),
        }
