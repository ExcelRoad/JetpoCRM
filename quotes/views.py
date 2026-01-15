from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from .models import Quote
from customers.models import Customer
from contacts.models import Contact
from projects.models import Project, ProjectBudget
from payments.models import Payment
from .forms import QuoteForm, ServiceFormSet, PaymentFormSet, QuoteServiceForm, QuotePaymentForm
from django.contrib.contenttypes.models import ContentType
from activities.models import Note
from django.http import JsonResponse
from django.template.loader import render_to_string


def quote_create(request, object_id, content_type):
    form = QuoteForm()
    service_formset = ServiceFormSet()
    payment_formset = PaymentFormSet()
    content_type_id = ContentType.objects.get(model = content_type).id
    contentType = ContentType.objects.get_for_id(content_type_id)
    targetObject = contentType.get_object_for_this_type(pk=object_id)
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        service_formset = ServiceFormSet(request.POST)
        payment_formset = PaymentFormSet(request.POST)

        if form.is_valid() and service_formset.is_valid() and payment_formset.is_valid():
            quote = form.save(commit=False)
            quote.content_object = targetObject
            quote.save()
            
            # Save services first
            services = service_formset.save(commit=False)
            
            # Create a map of index -> service instance
            service_map_by_index = {}
            
            # Manually save services with order and build map
            for i, s_form in enumerate(service_formset.forms):
                if s_form in service_formset.deleted_forms or (s_form.cleaned_data and s_form.cleaned_data.get('DELETE')):
                    if s_form.instance.pk:
                        s_form.instance.delete()
                    continue
                
                # Check if form has data (is valid/bound)
                if not s_form.is_valid() or not s_form.cleaned_data:
                    continue

                service = s_form.save(commit=False)
                service.quote = quote
                service.order = i  # Assign order based on formset position
                service.save()
                service_map_by_index[i] = service

            # Save and link payments
            for i, payment_form in enumerate(payment_formset.forms):
                if payment_form in payment_formset.deleted_forms or (payment_form.cleaned_data and payment_form.cleaned_data.get('DELETE')):
                    if payment_form.instance.pk:
                         payment_form.instance.delete()
                    continue
                
                if not payment_form.is_valid() or not payment_form.cleaned_data:
                     continue

                payment = payment_form.save(commit=False)
                payment.quote = quote
                payment.order = i
                
                service_identifier = payment_form.cleaned_data.get('quote_service')
                if service_identifier and str(service_identifier).isdigit():
                    service_idx = int(service_identifier)
                    if service_idx in service_map_by_index:
                        payment.quote_service = service_map_by_index[service_idx]
                
                payment.save()
                
            return redirect('quote-detail', quote.id)
    context = {
        'form': form,
        'service_formset': service_formset,
        'payment_formset': payment_formset,
        'form_header': 'יצירת הצעת מחיר',
        'contentType': contentType,
        'targetObject': targetObject
    }
    return render(request, 'quotes/quote-form.html', context)


def quote_edit(request, pk, fallback):
    quote = Quote.objects.get(pk=pk)
    form = QuoteForm(instance=quote)
    service_formset = ServiceFormSet(instance=quote)
    payment_formset = PaymentFormSet(instance=quote)
    
    # Pre-process payment forms to handle the service choices logic
    # We want to give the frontend an index or an ID it can understand
    # Ideally, we should pass the service order/index to the frontend
    # But for now, we'll let the frontend View handle the population logic via JS
    
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        service_formset = ServiceFormSet(request.POST, instance=quote)
        payment_formset = PaymentFormSet(request.POST, instance=quote)

        if form.is_valid() and service_formset.is_valid() and payment_formset.is_valid():
            form.save()
             # Create a map of {index: service_instance} based on forms position
            service_map_by_index = {}
            service_map_by_id = {}
            
            # Save services manually to ensure order is saved and map is built correctly
            for i, s_form in enumerate(service_formset.forms):
                if s_form in service_formset.deleted_forms or (s_form.cleaned_data and s_form.cleaned_data.get('DELETE')):
                    if s_form.instance.pk:
                        s_form.instance.delete()
                    continue

                if not s_form.is_valid() or not s_form.cleaned_data:
                    continue

                service = s_form.save(commit=False)
                service.quote = quote
                service.order = i
                service.save()
                
                service_map_by_index[i] = service
                service_map_by_id[str(service.pk)] = service
            
            
            for i, payment_form in enumerate(payment_formset.forms):
                 if payment_form in payment_formset.deleted_forms or (payment_form.cleaned_data and payment_form.cleaned_data.get('DELETE')):
                      if payment_form.instance.pk:
                          payment_form.instance.delete()
                      continue
                 
                 # Skip empty forms
                 if not payment_form.is_valid() or not payment_form.cleaned_data:
                      continue
                 
                 # Create/Update payment
                 payment = payment_form.save(commit=False)
                 payment.quote = quote # Ensure link
                 payment.order = i
                 
                 service_identifier = payment_form.cleaned_data.get('quote_service')
                 
                 if service_identifier:
                     service_identifier = str(service_identifier)
                     
                     # Case 1: Identifier acts as an ID (Existing service)
                     if service_identifier in service_map_by_id:
                         payment.quote_service = service_map_by_id[service_identifier]
                     
                     # Case 2: Identifier acts as an Index (New service or just indexed)
                     # ONLY if not found in by_id map (to avoid ID/Index collision if ID is small integer)
                     elif service_identifier.isdigit():
                         idx = int(service_identifier)
                         if idx in service_map_by_index:
                             payment.quote_service = service_map_by_index[idx]
                     
                 payment.save()

            if fallback == "lead-detail":
                return redirect('lead-detail', quote.content_object.id)
            if fallback == "customer-detail":
                return redirect('customer-detail', quote.content_object.id)
            elif fallback == 'quote-detail':
                return redirect('quote-detail', quote.id)
            else:
                return redirect(fallback)
    context = {
        'form': form,
        'service_formset': service_formset,
        'payment_formset': payment_formset,
        'form_header': 'עריכת הצעת מחיר',
        'contentType': quote.content_type,
        'targetObject': quote.content_object,
        'quote': quote
    }
    return render(request, 'quotes/quote-form.html', context)

def quote_delete(request, pk):
    if request.method == "POST":
        fallback = request.POST['fallback']
        quote = Quote.objects.get(pk=pk)
        object_id = quote.object_id
        quote.delete()
        if "detail" in fallback:
            return redirect(fallback, object_id)
        else:
            return redirect(fallback)


def quote_detail(request, pk):
    quote = Quote.objects.get(pk=pk)
    tagged_note = Note.objects.filter(
        content_type__model = 'quote',
        object_id = quote.id,
        tagged = True
    ).first()
    context = {
        'quote': quote,
        'tagged_note': tagged_note,
        'related_to_url': quote.content_type.model + "-detail"
    }
    return render(request, 'quotes/quote-detail.html', context)


def quote_submit_note(request, pk):
    quote = Quote.objects.get(pk = pk)
    note = Note.objects.create(
        text = request.POST['note'],
        content_object = quote
    )
    base_url = reverse('quote-detail', args=(pk,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def quote_delete_note(request, noteid):
    note = Note.objects.get(pk=noteid)
    quote = Quote.objects.get(pk=note.object_id)
    note.delete()
    base_url = reverse('quote-detail', args=(quote.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def quote_tag_note(request, noteid):
    # remove tag from all Notes for this Lead
    note = Note.objects.get(pk=noteid)
    if note.tagged:
        note.tagged = False
    else:
        all_notes = Note.objects.filter(object_id=note.content_object.id).update(tagged=False)
        note.tagged = True
    note.save()
    base_url = reverse('quote-detail', args=(note.content_object.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def quote_list(request):
    quotes = Quote.objects.all()

    context = {
        'quotes': quotes,
    }
    return render(request, 'quotes/quote-list.html', context)

def quote_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        quoteList = request.POST['quoteList']
        quoteList = quoteList.split(',')
        for l in quoteList:
            l = int(l)
            quote = Quote.objects.get(pk=l)
            quote.delete()
        return redirect(fallback)


def quote_kanban(request):
    all_quotes = Quote.objects.all()
    statuses = Quote.STATUSES
    status_dir = []
    for s in statuses:
        s_count = len(Quote.objects.filter(status=s[0]))
        status_dir.append(
            [s[0], s[1], s_count]
        )
    quotes = all_quotes
    context = {
        'quotes': quotes,
        'statuses': status_dir
    }
    return render(request, 'quotes/quote-kanban.html', context)


def quote_update_status(request):
    """
    AJAX endpoint to update quote status on drag-drop
    """
    # Validate AJAX POST Request
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        # Parse JSON body
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # Extract and validate lead_id
        quote_id = data.get('quote_id')
        if not quote_id:
            return JsonResponse({'success': False, 'error': 'Quote ID required'}, status=400)

        # Extract and validate status
        new_status = data.get('new_status', '').strip()
        valid_statuses = [s[0] for s in Quote.STATUSES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

        # Update database
        try:
            quote = Quote.objects.get(pk=quote_id)
            old_status = quote.status
            quote.status = new_status
            quote.save()
        except Quote.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Qutoe not found'}, status=404)

        # Calculate updated counts
        status_counts = {}
        for status_key, _ in Quote.STATUSES:
            status_counts[status_key] = Quote.objects.filter(status=status_key).count()

        # Return success with updated counts
        return JsonResponse({
            'success': True,
            'lead_id': quote_id,
            'old_status': old_status,
            'new_status': new_status,
            'status_counts': status_counts
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)


def quote_confirm(request, pk):
    """
    Confirm a quote: create customer/contact if needed, then create multiple projects
    (one per service line item) with associated payments
    """
    quote = Quote.objects.get(pk=pk)

    # Create or get the customer
    if quote.content_type == ContentType.objects.get_for_model(Customer):
        customer = quote.content_object
    else:
        # Convert lead to customer
        customer, created = Customer.objects.update_or_create(
            name = quote.content_object.company_name,
            defaults= {
                'lead_source': quote.content_object.lead_source,
            }
        )
        # create or get the contact (if lead)
        contact, created = Contact.objects.update_or_create(
            email = quote.content_object.email,
            phone = quote.content_object.phone,
            defaults= {
                'first_name' : quote.content_object.first_name,
                'last_name': quote.content_object.last_name,
                'role': quote.content_object.role,
                'customer': customer,
                'contact_type' : 'normal'
            }
        )

    # Create multiple projects (one per service line item)
    for quote_service in quote.quote_services.all():
        project = Project.objects.create(
            name = f"{quote.name} - {quote_service.name}",
            service = quote_service.service,
            status = 'open',
            customer = customer
        )
        # Create budget for each project
        ProjectBudget.objects.create(
            project = project,
            qty = quote_service.qty,
            price = quote_service.price,
            is_active = True,
            name = quote_service.name
        )

        # Create payments linked to this service's project
        for payment in quote_service.payments.all():
            Payment.objects.create(
                name = payment.name,
                service = quote_service.service,
                qty = 1,  # Payments don't have qty in quote
                price = payment.price,
                project = project,
                status = 'draft'
            )

    # update the quote to won
    quote.status = 'won'
    quote.save()
    # go to the customer page
    return redirect('customer-detail', customer.id)


def get_service_form_row(request):
    """
    AJAX endpoint to get a new service form row with proper Django widget rendering
    """
    if request.method == 'GET':
        form_index = request.GET.get('form_index', 0)
        form_prefix = request.GET.get('form_prefix', 'quote_service_set')

        # Create a new empty form with the correct prefix and index
        form = QuoteServiceForm(prefix=f'{form_prefix}-{form_index}')

        html = render_to_string('quotes/partials/service_form_row.html', {
            'service_form': form,
            'form_index': form_index,
            'row_number': int(form_index) + 1
        })

        return JsonResponse({'html': html, 'form_index': form_index})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_payment_form_row(request):
    """
    AJAX endpoint to get a new payment form row with proper Django widget rendering
    """
    if request.method == 'GET':
        form_index = request.GET.get('form_index', 0)
        form_prefix = request.GET.get('form_prefix', 'quote_payment_set')

        # Create a new empty form with the correct prefix and index
        form = QuotePaymentForm(prefix=f'{form_prefix}-{form_index}')

        # Add placeholder option to the payment service select
        form.fields['quote_service'].empty_label = 'בחר שירות'

        html = render_to_string('quotes/partials/payment_form_row.html', {
            'payment_form': form,
            'form_index': form_index,
            'row_number': int(form_index) + 1
        })

        return JsonResponse({'html': html, 'form_index': form_index})

    return JsonResponse({'error': 'Invalid request'}, status=400)

