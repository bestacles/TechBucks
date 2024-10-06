from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'is_class_transaction']  # Student is removed here

    def clean(self):
        cleaned_data = super().clean()
        is_class_transaction = cleaned_data.get('is_class_transaction')

        # Ensure the form is valid
        if is_class_transaction is None:
            raise forms.ValidationError("Transaction type must be specified.")

        return cleaned_data
