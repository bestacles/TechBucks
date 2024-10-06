from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'description', 'timestamp')  # Ensure timestamp is listed
