from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Customer
from .forms import CustomerForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.utils import export_to_excel
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from core.import_utils import generate_csv_template, parse_csv_row_count, get_csv_data
from activities.models import Note
from django.utils import timezone
from urllib.parse import urlencode

@login_required
def customer_import_template(request):
    return generate_csv_template(Customer)

@csrf_exempt
@login_required
def customer_import_preview(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        row_count = parse_csv_row_count(file.read())
        return JsonResponse({'success': True, 'row_count': row_count})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@login_required
def customer_import_confirm(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        data = get_csv_data(file.read())
        
        created_count = 0
        updated_count = 0
        failed_count = 0
        
        for row in data:
            try:
                # Normalize keys to lowercase for flexible matching
                row_lower = {str(k).lower().strip(): v for k, v in row.items()}
                
                def get_val(aliases):
                    for alias in aliases:
                        if alias.lower() in row_lower:
                            return row_lower[alias.lower()]
                    return None

                name = get_val(['name', 'שם לקוח', 'שם', 'לקוח', 'company', 'חברה'])
                if name:
                    name = str(name).strip()
                
                legal_id = get_val(['legal_id', 'ח.פ', 'ת.ז', 'מזהה'])
                if legal_id:
                    legal_id = str(legal_id).strip()
                
                if not name:
                    failed_count += 1
                    continue

                # Try matching existing customer for upsert
                customer = None
                if legal_id:
                    customer = Customer.objects.filter(legal_id=legal_id).first()
                if not customer:
                    customer = Customer.objects.filter(name=name).first()

                defaults = {
                    'name': name,
                    'legal_id': legal_id or '',
                    'sumit_id': get_val(['sumit_id', 'מזהה סומיט']) or '',
                    'folder_id': get_val(['folder_id', 'מזהה תיקייה']) or '',
                    'folder_link': get_val(['folder_link', 'קישור לתיקייה']) or '',
                    'description': get_val(['description', 'תיאור', 'הערות']) or '',
                    'website': get_val(['website', 'אתר']) or '',
                }

                if customer:
                    for key, value in defaults.items():
                        setattr(customer, key, value)
                    customer.save()
                    updated_count += 1
                else:
                    Customer.objects.create(**defaults)
                    created_count += 1

            except Exception as e:
                print(f"Error importing customer row: {e}")
                failed_count += 1
                
        return JsonResponse({
            'success': True, 
            'created': created_count, 
            'updated': updated_count, 
            'failed': failed_count
        })
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
    }
    return render(request, 'customers/customers-list.html', context)

@login_required
def customer_card(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
    }
    return render(request, 'customers/customers-card.html', context)

@login_required
def customer_create(request):
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            messages.success(request, 'לקוח נוצר בהצלחה', extra_tags=customer.name)
            return redirect('customer-detail', customer.id)
        else:
            messages.error(request, 'שגיאה ביצירת לקוח')
    context = {
        'form': form,
        'form_header': 'יצירת לקוח',
    }
    return render(request, 'customers/customer-form.html', context)

@login_required
def customer_edit(request, pk, fallback):
    customer = Customer.objects.get(pk=pk)
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'לקוח עודכן בהצלחה', extra_tags=customer.name)
            if fallback == "customer-detail":
                return redirect('customer-detail', customer.id)
            else:
                return redirect(fallback)
        else:
            messages.error(request, 'שגיאה בעדכון לקוח')
    context = {
        'form': form,
        'form_header': 'עריכת לקוח',
    }
    return render(request, 'customers/customer-form.html', context)

@login_required
def customer_export(request):
    if request.method == "POST":
        customerList = request.POST.get('customerList')
        if customerList:
            customer_ids = [int(id) for id in customerList.split(',')]
            customers = Customer.objects.filter(id__in=customer_ids)
            return export_to_excel(customers, filename_prefix="customers_export")
    return redirect('customer-list')

@login_required
def customer_delete(request, pk):
    if request.method == "POST":
        fallback = request.POST['fallback']
        customer = Customer.objects.get(pk=pk)
        customer.delete()
        messages.success(request, 'לקוח נמחק בהצלחה', extra_tags=customer.name)
        return redirect(fallback)

@login_required
def customer_detail(request, pk):
    customer = Customer.objects.get(pk=pk)
    tagged_note = customer.notes.all().filter(tagged=True).first()
    quote_total_price = 0
    quote_total_count = 0
    quote_active_price = 0
    quote_active_count = 0
    quote_won_price = 0
    quote_won_count = 0
    quote_lost_price = 0
    quote_lost_count = 0
    project_total_price = 0
    project_total_count = 0
    project_active_price = 0
    project_active_count = 0
    project_complete_count = 0
    project_complete_price = 0
    project_process_count = 0
    project_process_price = 0
    project_canceled_count = 0
    project_canceled_price = 0
    payment_total_count = 0
    payment_total_price = 0
    payment_draft_count = 0
    payment_draft_price = 0
    payment_billed_count = 0
    payment_billed_price = 0
    payment_paid_count = 0
    payment_paid_price = 0


    for p in customer.projects.all():
        project_total_price += p.budget['amount']
        project_total_count += 1
        if p.status == 'completed':
            project_complete_count += 1
            project_complete_price += p.budget['amount']
        if p.status == 'open':
            project_active_count += 1
            project_active_price += p.budget['amount']
        if p.status == 'canceled':
            project_canceled_count += 1
            project_canceled_price += p.budget['amount']
        for payment in p.payments.all():
            payment_total_count += 1
            payment_total_price += payment.total_price
            if payment.status == 'draft':
                payment_draft_count += 1
                payment_draft_price += payment.total_price
            if payment.status == 'billed':
                payment_billed_count += 1
                payment_billed_price += payment.total_price
            if payment.status == 'paid':
                payment_paid_count += 1
                payment_paid_price += payment.total_price

    projectInfo = {
        'total_price': project_total_price,
        'total_count': project_total_count,
        'active_price': project_active_price,
        'active_count': project_active_count,
        'complete_count': project_complete_count,
        'complete_price': project_complete_price,
        'canceled_price': project_canceled_price,
        'canceled_count': project_canceled_count
    }

    paymentInfo = {
        'total_count': payment_total_count,
        'total_price': payment_total_price,
        'draft_count': payment_draft_count,
        'draft_price': payment_draft_price,
        'billed_count': payment_billed_count,
        'billed_price': payment_billed_price,
        'paid_count': payment_paid_count,
        'paid_price': payment_paid_price,
    }

    for q in customer.quotes.all():
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
        'customer': customer,
        'tagged_note': tagged_note,
        'quoteInfo': quoteInfo,
        'projectInfo': projectInfo,
        'paymentInfo': paymentInfo,
        'today': timezone.now().date(),
    }
    return render(request, 'customers/customer-detail.html', context)

@login_required
def customer_submit_note(request, pk):
    customer = Customer.objects.get(pk = pk)
    note = Note.objects.create(
        text = request.POST['note'],
        content_object = customer
    )
    base_url = reverse('customer-detail', args=(pk,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

@login_required
def customer_delete_note(request, noteid):
    note = Note.objects.get(pk=noteid)
    customer = Customer.objects.get(pk=note.object_id)
    note.delete()
    messages.success(request, 'הערה נמחקה בהצלחה', extra_tags=customer.name)
    base_url = reverse('customer-detail', args=(customer.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

@login_required
def customer_tag_note(request, noteid):
    # remove tag from all Notes for this Lead
    note = Note.objects.get(pk=noteid)
    if note.tagged:
        note.tagged = False
    else:
        all_notes = Note.objects.filter(object_id=note.content_object.id).update(tagged=False)
        note.tagged = True
    note.save()
    base_url = reverse('customer-detail', args=(note.content_object.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

@login_required
def customer_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        customerList = request.POST['customerList']
        customerList = customerList.split(',')
        for l in customerList:
            l = int(l)
            customer = Customer.objects.get(pk=l)
            customer.delete()
        messages.success(request, f'{len(customerList)} לקוחות נמחקו בהצלחה')
        return redirect(fallback)
