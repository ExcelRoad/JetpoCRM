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
            'is_main': forms.CheckboxInput(attrs={'class': 'peer appearance-none w-11 h-5 bg-slate-100 rounded-full checked:bg-slate-800 cursor-pointer transition-colors duration-300'}),
            'is_alerts': forms.CheckboxInput(attrs={'class': 'peer appearance-none w-11 h-5 bg-slate-100 rounded-full checked:bg-slate-800 cursor-pointer transition-colors duration-300'}),
            'contact_type': CustomSelect(),
        }