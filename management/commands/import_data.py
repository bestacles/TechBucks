from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import pandas as pd
from students.models import Student
import qrcode
from io import BytesIO
from django.core.files import File

class Command(BaseCommand):
    help = 'Import students from an Excel file and auto-generate student IDs and accounts'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='The path to the Excel file to import')

    def generate_student_id(self, grade, count):
        year = '2024'  # You can use the current year dynamically
        unique_id = str(count).zfill(3)  # Zero-pad the count to 3 digits
        grade_number = str(grade).zfill(2)  # Zero-pad the grade to 2 digits (e.g., 02 for Grade 2)
        return f'{year}{grade_number}{unique_id}'  # No hyphens, continuous number

    def generate_qr_code(self, student):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(student.student_id)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_file = File(buffer, name=f'{student.student_id}_qr.png')
        student.qr_code.save(img_file.name, img_file, save=False)

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']

        # Load the Excel file and iterate over each sheet
        excel_data = pd.read_excel(excel_file, sheet_name=None)  # sheet_name=None loads all sheets as a dict

        count = 1  # Start the counter for student ID generation

        for sheet_name, data in excel_data.items():
            self.stdout.write(self.style.SUCCESS(f'Processing sheet: {sheet_name}'))

            for index, row in data.iterrows():
                first_name = row['first_name'].strip().lower()  # Make the username lowercase for consistency
                last_name = row['last_name'].strip().lower()  # Keep the last name for tracking purposes
                grade = row['grade']
                homeroom = row['homeroom']
                homeroom_teacher = row['homeroom_teacher']

                # Generate student ID
                student_id = self.generate_student_id(grade, count)

                # Extract the last three digits of the student ID for the username
                last_three_digits = student_id[-3:]
                username = f'{first_name}{last_three_digits}'  # Example: john001

                # Check if student already exists to avoid duplicates
                if not Student.objects.filter(first_name=first_name, last_name=last_name, grade=grade).exists():
                    # Create a user account for the student
                    password = User.objects.make_random_password()  # Generate a random password

                    user = User.objects.create_user(username=username, password=password)
                    user.first_name = first_name.capitalize()  # Capitalize the first letter of their name for display
                    user.last_name = last_name.capitalize()
                    user.save()

                    # Create the Student instance linked to the User
                    student = Student.objects.create(
                        user=user,
                        student_id=student_id,  # Use the generated student ID
                        first_name=first_name.capitalize(),
                        last_name=last_name.capitalize(),
                        grade=grade,
                        homeroom=homeroom,
                        homeroom_teacher=homeroom_teacher,
                        enrollment_status=True
                    )

                    # Generate QR code for the student and save it
                    self.generate_qr_code(student)
                    student.save()

                    self.stdout.write(self.style.SUCCESS(f'Successfully added {first_name.capitalize()} {last_name.capitalize()} with ID {student_id} and user account {username}'))
                    count += 1  # Increment the counter for the next student
                else:
                    self.stdout.write(self.style.WARNING(f'Student {first_name.capitalize()} {last_name.capitalize()} already exists'))
