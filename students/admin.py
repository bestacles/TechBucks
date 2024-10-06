# students/admin.py
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from .models import Student
from .forms import StudentImportForm
import pandas as pd
from transactions.models import Transaction


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

        count = 1  # Start the counter for student ID generation

        for sheet_name, data in excel_data.items():
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
                        student_id=student_id,
                        first_name=first_name,
                        last_name=last_name,
                        grade=grade,
                        homeroom=homeroom,
                        homeroom_teacher=homeroom_teacher,
                        qr_code='',  # Placeholder for QR code
                        enrollment_status=True
                    )
                    count += 1

    def generate_student_id(self, grade, count):
        # Generate student ID without hyphens: 2024GradeNumberUniqueID
        year = '2024'
        unique_id = str(count).zfill(3)  # Zero-pad the count to 3 digits
        grade_number = str(grade).zfill(2)  # Zero-padded grade (e.g., 02 for Grade 2)
        return f'{year}{grade_number}{unique_id}'

    # Adding a custom button to the admin changelist page
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = reverse('admin:import_students')
        return super(StudentAdmin, self).changelist_view(request, extra_context=extra_context)
