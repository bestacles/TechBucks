from django.db import models
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid
from students.models import Student

class Reward(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cost = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    unique_id = models.CharField(max_length=15, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='reward_qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = str(uuid.uuid4())[:8]  # Generate a short unique ID

        super().save(*args, **kwargs)

        # Generate and save QR code after saving the Reward instance
        self.generate_qr_code()

    def generate_qr_code(self):
        # Generate the QR code image
        qr = qrcode.make(f'Reward: {self.name} - Cost: {self.cost} - ID: {self.unique_id}')

        # Save the QR code to a BytesIO object
        qr_io = BytesIO()
        qr.save(qr_io, 'PNG')
        qr_file = ContentFile(qr_io.getvalue(), name=f'qr_code_{self.unique_id}.png')

        # Save the QR code to the qr_code field
        self.qr_code.save(f'qr_code_{self.unique_id}.png', qr_file)

    def __str__(self):
        return f"{self.name} ({self.unique_id})"


class Redemption(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='redemptions')  # Track student redemptions
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} redeemed {self.reward.name}"
