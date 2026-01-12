from django import forms
from .models import Customer
from .widgets import CustomFileInput, CustomSelect


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'legal_id', 'logo', 'sumit_id', 'folder_id','folder_link', 'description', 'lead_source', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'legal_id': forms.TextInput(attrs={'class': 'input-field'}),
            'sumit_id': forms.TextInput(attrs={'class': 'input-field'}),
            'folder_id': forms.TextInput(attrs={'class': 'input-field'}),
            'folder_link': forms.TextInput(attrs={'class': 'input-field'}),
            'logo': CustomFileInput(accept='image/*'),
            'description': forms.Textarea(attrs={'class': 'input-field'}),
            'lead_source': CustomSelect(),  # Custom searchable dropdown
            'website': forms.TextInput(attrs={'class': 'input-field'}),
        }