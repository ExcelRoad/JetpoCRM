from django import forms
from .models import Quote, Quote_Service, Quote_Payment
from django.forms.models import inlineformset_factory
from customers.widgets import StatusSelect, DynamicCustomSelect, CustomSelect


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'status': StatusSelect,  # Tom Select with colored pills
        }


class QuoteServiceForm(forms.ModelForm):
    class Meta:
        model = Quote_Service
        fields = ['service', 'name', 'qty', 'price', 'order']
        widgets = {
            'service': CustomSelect(attrs={'class': 'custom-select'}),  # CustomSelect searchable dropdown
            'name': forms.HiddenInput(),  # Auto-populated from service selection
            'qty': forms.NumberInput(attrs={'class': 'input-field'}),
            'price': forms.NumberInput(attrs={'class': 'input-field'}),
            'order': forms.HiddenInput(),
        }


class QuotePaymentForm(forms.ModelForm):
    quote_service = forms.CharField(required=False, widget=DynamicCustomSelect(attrs={'class': 'payment-service-select'}))

    class Meta:
        model = Quote_Payment
        fields = ['name', 'price', 'percent', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'price': forms.NumberInput(attrs={'class': 'input-field'}),
            'percent': forms.NumberInput(attrs={'class': 'w-full px-2 py-1.5 rounded-l-md bg-gray-50 border border-gray-200 focus:outline-gray-600', 'step': '0.01'}),
            'order': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.quote_service:
            # Populate the initial value for the extra field
            # Use the ID of the related Quote_Service
            self.fields['quote_service'].initial = self.instance.quote_service.id


ServiceFormSet = inlineformset_factory(
    Quote,
    Quote_Service,
    form = QuoteServiceForm,
    extra = 0,
    can_delete = True
)

PaymentFormSet = inlineformset_factory(
    Quote,
    Quote_Payment,
    form = QuotePaymentForm,
    extra = 0,
    can_delete = True
)
