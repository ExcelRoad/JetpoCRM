from django import forms
from leads.models import Lead, LeadSource
from customers.widgets import StatusSelect, CustomSelect


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'company_name',
            'status',
            'role',
            'lead_source',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-field'}),
            'last_name': forms.TextInput(attrs={'class': 'input-field'}),
            'email': forms.EmailInput(attrs={'class': 'input-field'}),
            'phone': forms.TextInput(attrs={'class': 'input-field'}),
            'company_name': forms.TextInput(attrs={'class': 'input-field'}),
            'status': StatusSelect(),  # Custom status dropdown with colored pills
            'role': forms.TextInput(attrs={'class': 'input-field'}),
            'lead_source': CustomSelect(allow_dynamic_options=True),  # Custom searchable dropdown with dynamic options
        }


class LeadSourceForm(forms.ModelForm):
    class Meta:
        model = LeadSource
        fields = [
            'name',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
        }