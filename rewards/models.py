from django.db import models
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid
from django.core.exceptions import ValidationError
from students.models import Student
from transactions.models import Transaction

class Reward(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cost = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    unique_id = models.CharField(max_length=15, unique=True, blank=True)
    qr_code = models.ImageField(upload_to='reward_qr_codes/', blank=True, null=True)

    def generate_qr_code(self):
        # Create a QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"data-to-encode")  # Replace this with actual data
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill='black', back_color='white')

        # Save it to a BytesIO object
        byte_io = BytesIO()
        img.save(byte_io, format='PNG')
        byte_io.seek(0)

        # Save the image to the model's ImageField
        self.qr_code.save(f'qr_code_{self.pk}.png', File(byte_io), save=False)
    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()  # Generate the QR code if it doesn't exist yet
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        # Generate data for the QR code
        qr_data = f"ID: {self.unique_id}"

        # Create the QR code instance
        qr = qrcode.QRCode(
            version=1,  # Keep version low since your data is small
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create an image from the QR code
        img = qr.make_image(fill='black', back_color='white')

        # Save the QR code image in memory
        qr_io = BytesIO()
        img.save(qr_io, 'PNG')

        # Save the QR code to the field
        qr_file = ContentFile(qr_io.getvalue(), name=f'qr_code_{self.unique_id}.png')
        self.qr_code.save(f'qr_code_{self.unique_id}.png', qr_file, save=False)

        # Save the instance again to update with the QR code (only the QR code field)
        super().save(update_fields=['qr_code'])

    def __str__(self):
        return f"{self.name} ({self.unique_id})"

class Redemption(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reward = models.ForeignKey('Reward', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)  # Add this if it should exist


    def save(self, *args, **kwargs):
        # Remove transaction creation from here
        # Instead, only perform validation if necessary
        total_techbucks = self.student.total_techbucks()
        reward_cost = self.reward.cost

        # Ensure values are integers for comparison
        if not isinstance(total_techbucks, int):
            total_techbucks = int(total_techbucks)
        if not isinstance(reward_cost, int):
            reward_cost = int(reward_cost)

        print(f"Total TechBucks: {total_techbucks}, Reward Cost: {reward_cost}")

        if total_techbucks >= self.reward.cost:
            super().save(*args, **kwargs)
        else:
            raise ValidationError("Not enough TechBucks to redeem this reward.")

    def __str__(self):
        return f"{self.student.first_name} redeemed {self.reward.name} on {self.redeemed_at}"

    def __str__(self):
        return f'Redeemed at: {self.redeemed_at}' if self.redeemed_at else 'Not redeemed yet'
