from tqdm import tqdm
import secrets
import string
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, reverse
from .models import Student
from .forms import StudentImportForm
import pandas as pd
from transactions.models import Transaction
import qrcode
from io import BytesIO
from django.core.files import File

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'grade', 'student_id', 'homeroom', 'homeroom_teacher')
    change_list_template = "admin/students/student/change_list.html"

    # Add custom action to handle file uploads and data import
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-students/', self.admin_site.admin_view(self.import_students), name='import_students'),
        ]
        return custom_urls + urls

    def import_students(self, request):
        if request.method == 'POST':
            form = StudentImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                self.handle_file_import(excel_file)
                self.message_user(request, "Students imported successfully!")
                return render(request, 'admin/import_students.html', {'form': form})

        form = StudentImportForm()
        return render(request, 'admin/import_students.html', {'form': form})

    def handle_file_import(self, excel_file):
        # Load the Excel file and iterate over each sheet
        excel_data = pd.read_excel(excel_file, sheet_name=None)  # sheet_name=None loads all sheets as a dict

        # Initialize count based on existing student IDs
        existing_ids = Student.objects.all().values_list('student_id', flat=True)
        existing_unique_ids = [int(sid[-3:]) for sid in existing_ids if len(sid) >= 9]  # '202405014' has length 9
        if existing_unique_ids:
            count = max(existing_unique_ids) + 1
        else:
            count = 1

        # Calculate the total number of rows for the progress bar
        total_rows = sum(len(data) for data in excel_data.values())

        with tqdm(total=total_rows, desc="Importing Students", unit="student") as pbar:
            for sheet_name, data in excel_data.items():
                for index, row in data.iterrows():
                    # Safely extract and clean data
                    first_name = str(row.get('first_name', '')).strip().lower()
                    last_name = str(row.get('last_name', '')).strip().lower()
                    grade = row.get('grade')
                    homeroom = str(row.get('homeroom', '')).strip()
                    homeroom_teacher = str(row.get('homeroom_teacher', '')).strip()

                    # Validate essential fields
                    if not first_name or not last_name or pd.isna(grade):
                        # Skip rows with essential missing information
                        pbar.update(1)
                        continue

                    # Ensure grade is an integer
                    try:
                        grade_int = int(grade)
                    except ValueError:
                        # Skip rows with invalid grade
                        pbar.update(1)
                        continue

                    # Generate student ID
                    student_id = self.generate_student_id(grade_int, count)

                    # Extract the last four digits of the student ID for the username
                    last_four_digits = self.get_last_four_digits(student_id, grade_int)
                    username = f'{first_name}{last_four_digits}'  # Example: john5014

                    # Check if user already exists based on username
                    user, user_created = User.objects.get_or_create(username=username)
                    if user_created:
                        # Create a user account for the student if it doesn't exist
                        password = self.generate_random_password()  # Generate a random password

                        user.set_password(password)
                        user.first_name = first_name.capitalize()  # Capitalize for display
                        user.last_name = last_name.capitalize()
                        user.save()

                        # Assign the user to the "Student" group
                        student_group, created = Group.objects.get_or_create(name='Student')
                        user.groups.add(student_group)
                    else:
                        # Update user's first and last name in case they have changed
                        user.first_name = first_name.capitalize()
                        user.last_name = last_name.capitalize()
                        user.save()

                    # Create or update the Student instance linked to the User
                    student, student_created = Student.objects.get_or_create(user=user, defaults={
                        'student_id': student_id,
                        'first_name': first_name.capitalize(),
                        'last_name': last_name.capitalize(),
                        'grade': grade_int,
                        'homeroom': homeroom,
                        'homeroom_teacher': homeroom_teacher,
                        'enrollment_status': True
                    })

                    if not student_created:
                        # Update existing student details
                        student.student_id = student_id
                        student.first_name = first_name.capitalize()
                        student.last_name = last_name.capitalize()
                        student.grade = grade_int
                        student.homeroom = homeroom
                        student.homeroom_teacher = homeroom_teacher
                        student.enrollment_status = True
                        student.save()

                    # Generate and save QR code for the student
                    self.generate_qr_code(student)

                    # Increment count to ensure unique student IDs and usernames
                    count += 1

                    # Update progress bar
                    pbar.update(1)

    def generate_student_id(self, grade, count):
        """
        Generate student ID in the format: 2024 + grade (2 digits) + unique_id (3 digits)
        Example: 202405014
        """
        year = '2024'
        unique_id = str(count).zfill(3)  # Zero-pad the count to 3 digits
        grade_number = str(grade).zfill(2)  # Zero-padded grade (e.g., 05 for Grade 5)
        return f'{year}{grade_number}{unique_id}'

    def get_last_four_digits(self, student_id, grade):
        """
        Extract the last four digits for the username:
        - Take the last digit of the grade
        - Concatenate with the unique_id (last 3 digits of student_id)
        Example: student_id = '202405014', grade = 5 → '5014'
        """
        grade_last_digit = str(grade)[-1]  # Get the last digit of the grade
        unique_id = student_id[-3:]  # Last 3 digits
        return f'{grade_last_digit}{unique_id}'

    def generate_qr_code(self, student):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(student.student_id)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_file = File(buffer, name=f'{student.student_id}_qr.png')
        student.qr_code.save(img_file.name, img_file, save=False)
        student.save()

    def generate_random_password(self, length=8):
        """
        Generate a secure random password using the secrets module.
        The password includes uppercase, lowercase letters, and digits.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    # Adding a custom button to the admin changelist page
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = reverse('admin:import_students')
        return super(StudentAdmin, self).changelist_view(request, extra_context=extra_context)
