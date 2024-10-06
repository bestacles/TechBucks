from django.core.management.base import BaseCommand
import pandas as pd
from students.models import Student

class Command(BaseCommand):
    help = 'Import students from an Excel file and auto-generate student IDs'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='The path to the Excel file to import')

    def generate_student_id(self, grade, count):
        year = '2024'  # You can use the current year dynamically
        unique_id = str(count).zfill(3)  # Zero-pad the count to 3 digits
        grade_number = str(grade).zfill(2)  # Zero-pad the grade to 2 digits (e.g., 02 for Grade 2)
        return f'{year}{grade_number}{unique_id}'  # No hyphens, continuous number

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']

        # Load the Excel file and iterate over each sheet
        excel_data = pd.read_excel(excel_file, sheet_name=None)  # sheet_name=None loads all sheets as a dict

        count = 1  # Start the counter for student ID generation

        for sheet_name, data in excel_data.items():
            self.stdout.write(self.style.SUCCESS(f'Processing sheet: {sheet_name}'))

            for index, row in data.iterrows():
                first_name = row['first_name']
                last_name = row['last_name']
                grade = row['grade']
                homeroom = row['homeroom']
                homeroom_teacher = row['homeroom_teacher']

                # Generate student ID
                student_id = self.generate_student_id(grade, count)

                # Check if student already exists to avoid duplicates
                if not Student.objects.filter(first_name=first_name, last_name=last_name, grade=grade).exists():
                    Student.objects.create(
                        student_id=student_id,  # Use the generated student ID
                        first_name=first_name,
                        last_name=last_name,
                        grade=grade,
                        homeroom=homeroom,
                        homeroom_teacher=homeroom_teacher,
                        qr_code='',  # Placeholder for QR code
                        enrollment_status=True
                    )
                    self.stdout.write(self.style.SUCCESS(f'Successfully added {first_name} {last_name} with ID {student_id}'))
                    count += 1  # Increment the counter for the next student
                else:
                    self.stdout.write(self.style.WARNING(f'Student {first_name} {last_name} already exists'))
