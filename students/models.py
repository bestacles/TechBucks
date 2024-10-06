# students/models.py
from django.contrib.auth.models import User
from django.db import models
import qrcode
from io import BytesIO
from django.db.models import Sum
from django.core.files import File
from PIL import Image


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    student_id = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    grade = models.CharField(max_length=2)
    homeroom = models.CharField(max_length=100)
    homeroom_teacher = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/students/', null=True, blank=True)
    enrollment_status = models.BooleanField(default=True)  # Add this field

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.student_id)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_file = File(buffer, name=f'{self.student_id}_qr.png')
        self.qr_code.save(img_file.name, img_file, save=False)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self.generate_student_id()
        self.generate_qr_code()
        super().save(*args, **kwargs)

    def generate_student_id(self):
        school_year = "2024"
        grade_code = str(self.grade).zfill(2)  # Convert grade to a string
        existing_students = Student.objects.filter(grade=self.grade).count()
        student_number = str(existing_students + 1).zfill(3)
        return f"{school_year}{grade_code}{student_number}"

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.student_id}'

    def total_techbucks(self):
        transactions = self.transactions.all()
        total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        return total if total else 0
