from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
import json
from django.http import JsonResponse
from .models import Lead, LeadSource
from .forms import LeadForm, LeadSourceForm
from activities.models import Note


def lead_list(request):
    all_leads = Lead.objects.all()

    leads = all_leads
    context = {
        'leads': leads
    }
    return render(request, 'leads/leads-list.html', context)

def lead_kanban(request):
    all_leads = Lead.objects.all()
    statuses = Lead.LEAD_STATUSES
    status_dir = []
    for s in statuses:
        s_count = len(Lead.objects.filter(status=s[0]))
        status_dir.append(
            [s[0], s[1], s_count]
        )
    leads = all_leads
    context = {
        'leads': leads,
        'statuses': status_dir
    }
    return render(request, 'leads/leads-kanban.html', context)

def lead_create(request):
    form = LeadForm()
    leadSources = list(LeadSource.objects.values('id', 'name'))
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            return redirect('lead-detail', lead.id)
    context = {
        'form': form,
        'form_header': 'יצירת ליד',
        'leadSources': json.dumps(leadSources),
    }
    return render(request, 'leads/lead-form.html', context)

def lead_edit(request, pk, fallback):
    lead = Lead.objects.get(pk=pk)
    leadSources = list(LeadSource.objects.values('id', 'name'))
    form = LeadForm(
        instance=lead
    )
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            if fallback == 'lead-detail':
                return redirect(fallback, lead.id)
            elif fallback in ['lead-list', 'lead-kanban']:
                return redirect(fallback)  
    context = {
        'lead': lead,
        'form': form,
        'form_header': 'עריכת ליד',
        'leadSources': json.dumps(leadSources),
    }
    return render(request, 'leads/lead-form.html', context)

def lead_delete(request, pk):
    if request.method == "POST":
        fallback = request.POST['fallback']
        lead = Lead.objects.get(pk=pk)
        lead.delete()
        return redirect(fallback)

def lead_convert(request, pk):
    lead = Lead.objects.get(pk=pk)
    # create customer
    from customers.models import Customer
    from contacts.models import Contact
    customer, created = Customer.objects.update_or_create(
        name = lead.company_name,
        defaults= {
            'lead_source': lead.lead_source,
        }
    )
    # pass all the Notes to the new Customer
    for note in lead.notes.all():
        note.content_object = customer
        note.save()
    # pass all Quotes to the new Customer
    for quote in lead.quotes.all():
        quote.content_object = customer
        quote.save()

    # Create Contact
    contact, created = Contact.objects.update_or_create(
        email = lead.email,
        phone = lead.phone,
        defaults= {
            'first_name' : lead.first_name,
            'last_name': lead.last_name,
            'role': lead.role,
            'customer': customer,
            'contact_type' : 'normal'
        }
    )

    # Update the lead info
    lead.status = 'won'
    lead.save()

    return redirect('customer-detail', customer.id)


def lead_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        leadList = request.POST['leadList']
        leadList = leadList.split(',')
        for l in leadList:
            l = int(l)
            lead = Lead.objects.get(pk=l)
            lead.delete()
        return redirect(fallback)

def lead_detail(request, pk):
    lead = Lead.objects.get(pk=pk)
    tagged_note = lead.notes.all().filter(tagged=True).first()
    quote_total_price = 0
    quote_total_count = 0
    quote_active_price = 0
    quote_active_count = 0
    quote_won_price = 0
    quote_won_count = 0
    quote_lost_price = 0
    quote_lost_count = 0

    for q in lead.quotes.all():
        quote_total_price += q.total_price
        quote_total_count += 1
        if (q.status == 'draft' or q.status == 'sent'):
            quote_active_price += q.total_price
            quote_active_count += 1
        elif q.status == 'won':
            quote_won_price += q.total_price
            quote_won_count += 1
        elif q.status == 'lost':
            quote_lost_price += q.total_price
            quote_lost_count += 1

            
    quoteInfo = {
        'total_price': quote_total_price,
        'total_count': quote_total_count,
        'active_price': quote_active_price,
        'active_count': quote_active_count,
        'won_price': quote_won_price,
        'won_count': quote_won_count,
        'lost_count': quote_lost_count,
        'lost_price': quote_lost_price,
    }
    context = {
        'lead': lead,
        'tagged_note' : tagged_note,
        'quoteInfo': quoteInfo
    }
    return render(request, 'leads/lead-detail.html', context)

def lead_source_create(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            name = request.POST.get('name', '').strip()
            if not name:
                error = 'שם מקור ליד הינו חובה'
                return JsonResponse({
                    'error': error
                }, status = 400)
            
            if LeadSource.objects.filter(name__iexact=name).exists():
                error = 'קיים מקור ליד עם שם זה'
                return JsonResponse({
                    'error': error
                }, status=400)
            
            
            lead_source = LeadSource.objects.create(
                name = name
            )

            return JsonResponse({
                'success': True,
                'id': lead_source.id,
                'name': lead_source.name
            })
    return JsonResponse({'error': 'Invalid Request'}, status=400)

def lead_submit_note(request, pk):
    lead = Lead.objects.get(pk = pk)
    note = Note.objects.create(
        text = request.POST['note'],
        content_object = lead
    )
    base_url = reverse('lead-detail', args=(pk,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def lead_delete_note(request, noteid):
    note = Note.objects.get(pk=noteid)
    lead = Lead.objects.get(pk=note.object_id)
    note.delete()
    base_url = reverse('lead-detail', args=(lead.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def lead_tag_note(request, noteid):
    # remove tag from all Notes for this Lead
    note = Note.objects.get(pk=noteid)
    if note.tagged:
        note.tagged = False
    else:
        all_notes = Note.objects.filter(object_id=note.content_object.id).update(tagged=False)
        note.tagged = True
    note.save()
    base_url = reverse('lead-detail', args=(note.content_object.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def lead_update_status(request):
    """
    AJAX endpoint to update lead status on drag-drop
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
        lead_id = data.get('lead_id')
        if not lead_id:
            return JsonResponse({'success': False, 'error': 'Lead ID required'}, status=400)

        # Extract and validate status
        new_status = data.get('new_status', '').strip()
        valid_statuses = [s[0] for s in Lead.LEAD_STATUSES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

        # Update database
        try:
            lead = Lead.objects.get(pk=lead_id)
            old_status = lead.status
            lead.status = new_status
            lead.save()
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lead not found'}, status=404)

        # Calculate updated counts
        status_counts = {}
        for status_key, _ in Lead.LEAD_STATUSES:
            status_counts[status_key] = Lead.objects.filter(status=status_key).count()

        # Return success with updated counts
        return JsonResponse({
            'success': True,
            'lead_id': lead_id,
            'old_status': old_status,
            'new_status': new_status,
            'status_counts': status_counts
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=405)