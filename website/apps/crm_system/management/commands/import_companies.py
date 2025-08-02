import pandas as pd
from django.core.management import BaseCommand, CommandError
from django.db import transaction

from apps.crm_system.models import (
    Canton,
    Company,
    CompanyContactRecord,
    CompanyType,
    LegalForm,
    LegalSeat,
)


class Command(BaseCommand):
    help = "Import companies"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            required=True
        )
        parser.add_argument(
            '--title',
            required=True
        )
        parser.add_argument(
            '--status',
            required=False
        )
        parser.add_argument(
            '--type',
            required=True
        )
        parser.add_argument(
            '--description',
            required=False
        )
        parser.add_argument(
            '--liquidation',
            required=False
        )
        parser.add_argument(
            '--canton',
            required=True
        )
        parser.add_argument(
            '--legal_seat',
            required=True
        )
        parser.add_argument(
            '--legal_form',
            required=True
        )
        parser.add_argument(
            '--visited',
            required=False
        )

    def handle(self, *args, **options):
        file_path = options['file']
        visited_option = options.get('visited')
        companies = []
        CompanyContactRecord.objects.all().delete()
        Company.objects.all().delete()
        try:
            df = pd.read_excel(file_path, sheet_name=None)
        except FileNotFoundError as e:
            raise CommandError('File not found') from e

        if not len(df):
            raise CommandError('Provided file is empty')

        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS('Reading file...'))
            for sheet in df.keys():
                df[sheet].fillna('', inplace=True)
                for _, row in df[sheet].iterrows():
                    title = row[options['title']]
                    description = row.get(options['description'], '')
                    in_liquidation = bool(row.get(options['liquidation'], False))
                    canton_name = row[options['canton']]
                    company_type_name = row[options['type']]
                    legal_seat_name = row[options['legal_seat']]
                    legal_form_name = row[options['legal_form']]

                    canton, _ = Canton.objects.get_or_create(
                        name=canton_name,
                    )
                    company_type, _ = CompanyType.objects.get_or_create(
                        name=company_type_name,
                    )
                    legal_seat, _ = LegalSeat.objects.get_or_create(
                        name=legal_seat_name,
                    )
                    legal_form, _ = LegalForm.objects.get_or_create(
                        name=legal_form_name
                    )
                    company = Company(
                        title=title,
                        type=company_type,
                        description=description,
                        in_liquidation=in_liquidation,
                        canton=canton,
                        legal_seat=legal_seat,
                        legal_form=legal_form,
                    )
                    if visited_option and bool(row[visited_option]):
                        company.save()
                        status = options['status'] or ''
                        CompanyContactRecord.objects.create(
                            company_id=company.pk,
                            status=status
                        )
                        continue
                    companies.append(company)

            self.stdout.write(self.style.SUCCESS('Loading data into database...'))
            Company.objects.bulk_create(companies)
            self.stdout.write(self.style.SUCCESS('Successfully imported companies'))
