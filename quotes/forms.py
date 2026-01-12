from django import forms
from .models import Quote, Quote_Service, Quote_Payment
from django.forms.models import inlineformset_factory


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'status': forms.Select(attrs={'class': 'status-select'}),  # Tom Select with colored pills
        }


class QuoteServiceForm(forms.ModelForm):
    class Meta:
        model = Quote_Service
        fields = ['service', 'name', 'qty', 'price', 'order']
        widgets = {
            'service': forms.Select(attrs={'class': 'custom-select'}),  # Tom Select searchable dropdown
            'name': forms.HiddenInput(),  # Auto-populated from service selection
            'qty': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'price': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'order': forms.HiddenInput(),
        }


class QuotePaymentForm(forms.ModelForm):
    class Meta:
        model = Quote_Payment
        fields = ['quote_service', 'name', 'price', 'percent', 'order']
        widgets = {
            'quote_service': forms.Select(attrs={'class': 'payment-service-select'}),  # Tom Select, populated dynamically by JS
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'price': forms.NumberInput(attrs={'class': 'input-field', 'step': '0.01'}),
            'percent': forms.NumberInput(attrs={'class': 'w-full px-2 py-1.5 rounded-l-md bg-gray-50 border border-gray-200 focus:outline-gray-600', 'step': '0.01'}),
            'order': forms.HiddenInput(),
        }


ServiceFormSet = inlineformset_factory(
    Quote,
    Quote_Service,
    form = QuoteServiceForm,
    extra = 1,
    can_delete = True
)

PaymentFormSet = inlineformset_factory(
    Quote,
    Quote_Payment,
    form = QuotePaymentForm,
    extra = 1,
    can_delete = True
)
