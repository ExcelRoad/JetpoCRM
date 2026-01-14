import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from customers.models import Customer
from quotes.models import Quote

User = get_user_model()

# Setup data
user = User.objects.first()
if not user:
    user = User.objects.create_user('testuser', 'test@example.com', 'password')

customer, _ = Customer.objects.get_or_create(name="Test Customer")
ct = ContentType.objects.get_for_model(Customer)

from activities.models import Service

# Create a service
service_obj, _ = Service.objects.get_or_create(
    name="Test Service", 
    defaults={
        'default_price': 100,
        'default_qty': 1,
        'budget_type': 'fix'
    }
)

# Prepare POST data simulating the formset
data = {
    'name': 'Test Quote',
    'status': 'draft',
    
    # Service Formset (Management Form)
    'quote_services-TOTAL_FORMS': '1',
    'quote_services-INITIAL_FORMS': '0',
    'quote_services-MIN_NUM_FORMS': '0',
    'quote_services-MAX_NUM_FORMS': '1000',
    
    # Service 0
    'quote_services-0-service': service_obj.id, 
    'quote_services-0-name': 'Service 1',
    'quote_services-0-qty': '1',
    'quote_services-0-price': '100',
    'quote_services-0-order': '0',
    'quote_services-0-DELETE': '',

    # Payment Formset (Management Form)
    'quote_payments-TOTAL_FORMS': '1',
    'quote_payments-INITIAL_FORMS': '0',
    'quote_payments-MIN_NUM_FORMS': '0',
    'quote_payments-MAX_NUM_FORMS': '1000',
    
    # Payment 0 (Linked to Service 0 via index "0")
    'quote_payments-0-quote_service': '0', 
    'quote_payments-0-name': 'Payment 1',
    'quote_payments-0-price': '50',
    'quote_payments-0-percent': '50',
    'quote_payments-0-order': '0',
    'quote_payments-0-DELETE': '',
}

client = Client()
client.force_login(user)

print("Attempting to create quote...")
try:
    # URL pattern: quotes/<content_type>/<object_id>/create
    response = client.post(f'/quotes/{ct.model}/{customer.id}/create', data, HTTP_HOST='127.0.0.1')
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 302:
        print("Success! Redirected.")
        
        # Verify DB
        quote = Quote.objects.filter(name='Test Quote').last()
        if quote:
            print(f"Quote created: {quote}")
            services = quote.quote_services.all()
            payments = quote.quote_payments.all()
            print(f"Services count: {services.count()}")
            print(f"Payments count: {payments.count()}")
            
            if payments.exists() and services.exists():
                payment = payments.first()
                service = services.first()
                if payment.quote_service == service:
                    print("VERIFICATION PASSED: Payment is correctly linked to Service!")
                else:
                    print(f"VERIFICATION FAILED: Payment link mismatch. Payment service: {payment.quote_service}, Expected: {service}")
            elif not services.exists():
                print("VERIFICATION FAILED: Services not saved.")
            elif not payments.exists():
                print("VERIFICATION FAILED: Payments not saved.")
        else:
            print("VERIFICATION FAILED: Quote not found in DB.")
    else:
        print("Failed to create quote. Form likely invalid.")
        if response.context:
            if 'form' in response.context:
                print(f"Main Form Errors: {response.context['form'].errors}")
            if 'service_formset' in response.context:
                print(f"Service Formset Errors: {response.context['service_formset'].errors}")
                print(f"Service Formset Non-Form Errors: {response.context['service_formset'].non_form_errors()}")
            if 'payment_formset' in response.context:
                print(f"Payment Formset Errors: {response.context['payment_formset'].errors}")
                print(f"Payment Formset Non-Form Errors: {response.context['payment_formset'].non_form_errors()}")
        else:
            print("Response context is missing. Response content snippet:")
            print(response.content[:200])

except Exception as e:
    print(f"An error occurred: {e}")
