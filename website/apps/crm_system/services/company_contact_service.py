from django.utils import timezone

from apps.crm_system.models import Company, CompanyContactRecord


class CompanyContactService:
    @staticmethod
    def add_contact_record(user, company: Company) -> CompanyContactRecord:
        record = CompanyContactRecord.objects.create(
            user=user,
            company=company,
            contacted_at=timezone.now(),
        )
        return record
