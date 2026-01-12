from django import forms
from .models import Project, ProjectBudget
from customers.widgets import StatusSelect, CustomSelect

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'status', 'service', 'customer', 'folder_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'folder_id': forms.TextInput(attrs={'class': 'input-field'}),
            'customer': CustomSelect(),
            'service': CustomSelect(),  # Custom searchable dropdown
            'status': StatusSelect(),  # Custom status dropdown with colored pills
        }


class ProjectBudgetForm(forms.ModelForm):
    class Meta:
        model = ProjectBudget
        fields = [
            'qty', 'price'
        ]
        widgets = {
            'qty' : forms.NumberInput(attrs={'class': 'input-field'}),
            'price' : forms.NumberInput(attrs={'class': 'input-field'}),
        }