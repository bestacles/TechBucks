from django.db import models
from students.models import Student
from django.contrib.auth.models import User

class Transaction(models.Model):
    student = models.ForeignKey(Student, related_name='transactions', on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    description = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_class_transaction = models.BooleanField(default=False)
    performed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)  # The teacher or user who performed the transaction

    def __str__(self):
        return f"{self.student} - {self.amount} TechBucks on {self.timestamp}"

    def save(self, *args, **kwargs):
        print(f"Saving Transaction: {self.amount} performed by {self.performed_by}")
        super().save(*args, **kwargs)
