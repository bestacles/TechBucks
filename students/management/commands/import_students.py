from django.core.management.base import BaseCommand
import pandas as pd
from students.models import Student

class Command(BaseCommand):
    help = 'Import students from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='The path to the Excel file to import')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']

        # Load the Excel file and iterate over each sheet
        excel_data = pd.read_excel(excel_file, sheet_name=None)  # sheet_name=None loads all sheets as a dict

        for sheet_name, data in excel_data.items():
            self.stdout.write(self.style.SUCCESS(f'Processing sheet: {sheet_name}'))

            for index, row in data.iterrows():
                first_name = row['first_name']
                last_name = row['last_name']
                grade = row['grade']
                homeroom = row['homeroom']
                homeroom_teacher = row['homeroom_teacher']

                # Check if student already exists to avoid duplicates
                if not Student.objects.filter(first_name=first_name, last_name=last_name, grade=grade).exists():
                    Student.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        grade=grade,
                        homeroom=homeroom,
                        homeroom_teacher=homeroom_teacher,
                        qr_code='',  # Placeholder for QR code
                        enrollment_status=True
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully added {first_name} {last_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Student {first_name} {last_name} already exists'))
