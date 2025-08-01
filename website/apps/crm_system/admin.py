from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from apps.core.admin import AdminModelPermissionMixin
from .models import *

# Register your models here.

User = get_user_model()


class CompanyContactRecordStacked(AdminModelPermissionMixin, admin.StackedInline):
    model = CompanyContactRecord
    readonly_fields = ['user', 'contacted_at']
    permissions = {
        User.Status.MANAGER: '__all__',
        User.Status.OPERATOR: '__all__',
    }
    extra = 0


class CompanyNoteStacked(AdminModelPermissionMixin, admin.StackedInline):
    model = CompanyNote
    readonly_fields = ['user']
    permissions = {
        User.Status.MANAGER: '__all__',
        User.Status.OPERATOR: '__all__',
    }
    extra = 0


class IsReadyStatusFilter(admin.SimpleListFilter):
    title = _('Company ready')
    parameter_name = 'is_company_ready'

    class LookupChoices(TextChoices):
        YES = 'yes', _('Yes')

    def lookups(self, request, model_admin):
        return self.LookupChoices.choices

    def queryset(self, request, queryset):
        value = self.value()
        if value == self.LookupChoices.YES:
            return queryset.filter_contact_ready_status(status=True)
        return queryset


class LastContactStatusFilter(admin.SimpleListFilter):
    title = _('Last contact status')
    parameter_name = 'last_contact_status'

    def lookups(self, request, model_admin):
        return CompanyContactRecord.Status.choices

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter_last_contact_status(status=value)
        return queryset


@admin.register(Company)
class CompanyAdmin(AdminModelPermissionMixin, admin.ModelAdmin):
    search_fields = ['title']
    search_help_text = _('Type company name')
    autocomplete_fields = ['type', 'legal_form', 'legal_seat', 'canton']
    list_filter = [
        'canton',
        'legal_seat',
        'legal_form',
        'in_liquidation',
        LastContactStatusFilter,
        IsReadyStatusFilter,
        'created_at',
    ]
    list_display = [
        'title',
        'description',
        'in_liquidation',
        'display_last_contact_status',
        'website',
        'phone',
        'email',
        'canton',
        'legal_seat',
        'legal_form',
        'created_at',
    ]
    date_hierarchy = 'created_at'
    inlines = [CompanyNoteStacked, CompanyContactRecordStacked]
    permissions = {
        User.Status.MANAGER: '__all__',
        User.Status.OPERATOR: ['change', 'view', 'module'],
    }

    @admin.display(description=_('Last contact status'))
    def display_last_contact_status(self, obj):
        return obj.contact_records.latest('contacted_at').get_status_display()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        if issubclass(formset.model, (CompanyContactRecord, CompanyNote)):
            for instance in instances:
                if not instance.pk:
                    instance.user = request.user
        super().save_formset(request, form, formset, change)

    def change_view(self, request, object_id, *args, **kwargs):
        extra_context = {
            'show_google_search': True,
        }
        kwargs['extra_context'] = extra_context
        return super().change_view(request, object_id, *args, **kwargs)


@admin.register(CompanyType)
class CompanyTypeAdmin(AdminModelPermissionMixin, admin.ModelAdmin):
    search_fields = ['name']
    permissions = {
        User.Status.MANAGER: '__all__',
        User.Status.OPERATOR: '__all__',
    }


@admin.register(LegalForm)
class LegalFormAdmin(AdminModelPermissionMixin, admin.ModelAdmin):
    search_fields = ['name']
    permissions = {
        User.Status.MANAGER: '__all__',
        User.Status.OPERATOR: '__all__',
    }


@admin.register(LegalSeat)
class LegalSeatAdmin(AdminModelPermissionMixin, admin.ModelAdmin):
    search_fields = ['name']
    permissions = {
        User.Status.MANAGER: '__all__',
        User.Status.OPERATOR: '__all__',
    }


@admin.register(Canton)
class CantonAdmin(AdminModelPermissionMixin, admin.ModelAdmin):
    search_fields = ['name']
    permissions = {
        User.Status.MANAGER: '__all__',
        User.Status.OPERATOR: ['view'],
    }
