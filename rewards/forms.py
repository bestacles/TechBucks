# forms.py
from django import forms
from .models import Reward

class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ['name', 'description', 'cost', 'category']

class XLSXUploadForm(forms.Form):
    xlsx_file = forms.FileField()
