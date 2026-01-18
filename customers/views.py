from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from .models import Customer
from .forms import CustomerForm
from activities.models import Note


def customer_list(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
    }
    return render(request, 'customers/customers-list.html', context)

def customer_card(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
    }
    return render(request, 'customers/customers-card.html', context)

def customer_create(request):
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            return redirect('customer-detail', customer.id)
    context = {
        'form': form,
        'form_header': 'יצירת לקוח',
    }
    return render(request, 'customers/customer-form.html', context)

def customer_edit(request, pk, fallback):
    customer = Customer.objects.get(pk=pk)
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            if fallback == "customer-detail":
                return redirect('customer-detail', customer.id)
            else:
                return redirect(fallback)
    context = {
        'form': form,
        'form_header': 'עריכת לקוח',
    }
    return render(request, 'customers/customer-form.html', context)

def customer_delete(request, pk):
    if request.method == "POST":
        fallback = request.POST['fallback']
        customer = Customer.objects.get(pk=pk)
        customer.delete()
        return redirect(fallback)

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
    }
    return render(request, 'customers/customer-detail.html', context)

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

def customer_delete_note(request, noteid):
    note = Note.objects.get(pk=noteid)
    customer = Customer.objects.get(pk=note.object_id)
    note.delete()
    base_url = reverse('customer-detail', args=(customer.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

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

def customer_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        customerList = request.POST['customerList']
        customerList = customerList.split(',')
        for l in customerList:
            l = int(l)
            customer = Customer.objects.get(pk=l)
            customer.delete()
        return redirect(fallback)
