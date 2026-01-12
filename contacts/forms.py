from django import forms
from .models import Contact
from customers.widgets import CustomSelect


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone', 'role', 'customer', 'is_alerts', 'is_main', 'contact_type']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-field'}),
            'last_name': forms.TextInput(attrs={'class': 'input-field'}),
            'email': forms.EmailInput(attrs={'class': 'input-field'}),
            'phone': forms.TextInput(attrs={'class': 'input-field'}),
            'role': forms.TextInput(attrs={'class': 'input-field'}),
            'customer': CustomSelect(),  # Custom searchable dropdown
            'is_main': forms.CheckboxInput(attrs={'class': 'input-checkbox'}),
            'is_alerts': forms.CheckboxInput(attrs={'class': 'input-checkbox'}),
            'contact_type': CustomSelect(),
        }