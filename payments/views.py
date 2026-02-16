from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode
from .models import Payment
from django.contrib import messages
from projects.models import Project
from django.contrib.auth.decorators import login_required
from core.utils import export_to_excel

@login_required
def payment_edit(request, pk, main = False):
    if request.method == "POST":
        payQty = request.POST['paymentQty']
        payPrice = request.POST['paymentPrice']
        payName = request.POST['paymentName']
        payExpectedDate = request.POST.get('paymentExpectedDate')
        if payExpectedDate == '':
            payExpectedDate = None
        projectId = request.POST.get('project', 0)
        fallback = request.POST.get('fallback', 'payment-list')
        if pk != 0 and pk != '0':
            payment = Payment.objects.get(pk=pk)
            payment.qty = payQty
            payment.price = payPrice
            payment.name = payName
            payment.expected_date = payExpectedDate
            payment.save()
            messages.success(request, 'תשלום נשמר בהצלחה', extra_tags=payment.name)
        else:
            project = Project.objects.get(pk = int(projectId))
            payment = Payment.objects.create(
                name = payName,
                service = project.service,
                project = project,
                qty = payQty,
                price = payPrice,
                expected_date = payExpectedDate,
                status = 'draft'
            )
            messages.success(request, 'תשלום נוצר בהצלחה', extra_tags=payment.name)
        
        if fallback == 'payment-list':
            return redirect('payment-list')
        elif fallback == 'project-detail':
            base_url = reverse('project-detail', args=(payment.project.id,))
            query_string = urlencode({'section': 'payments'})
            return redirect(f'{base_url}?{query_string}')
        elif fallback == 'customer-detail':
            base_url = reverse('customer-detail', args=(payment.project.customer.id,))
            query_string = urlencode({'section': 'payments'})
            return redirect(f'{base_url}?{query_string}')
        else:
            # support direct reverse lookups or fallback to payment-list
            try:
                return redirect(fallback)
            except:
                return redirect('payment-list')

@login_required
def payment_delete(request, pk):
    payment = Payment.objects.get(pk=pk)
    project_id = payment.project.id
    customer_id = payment.project.customer.id
    payment.delete()
    messages.success(request, 'תשלום נמחק בהצלחה', extra_tags=payment.name)
    
    fallback = request.POST.get('fallback', 'payment-list')
    if fallback == 'payment-list':
        return redirect('payment-list')
    elif fallback == 'project-detail':
        base_url = reverse('project-detail', args=(project_id,))
        query_string = urlencode({'section': 'payments'})
        return redirect(f'{base_url}?{query_string}')
    elif fallback == 'customer-detail':
        base_url = reverse('customer-detail', args=(customer_id,))
        query_string = urlencode({'section': 'payments'})
        return redirect(f'{base_url}?{query_string}')
    else:
        try:
            return redirect(fallback)
        except:
            return redirect('payment-list')

@login_required
def payment_list(request):
    payments = Payment.objects.all()
    context = {
        'payments': payments,
        'today': timezone.now().date(),
    }
    return render(request, 'payments/payment-list.html', context)

@login_required
def payment_export(request):
    if request.method == "POST":
        paymentList = request.POST.get('paymentList')
        if paymentList:
            payment_ids = [int(id) for id in paymentList.split(',')]
            payments = Payment.objects.filter(id__in=payment_ids)
            return export_to_excel(payments, filename_prefix="payments_export")
    return redirect('payment-list')

@login_required
def payment_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        paymentList = request.POST['paymentList']
        paymentList = paymentList.split(',')
        for l in paymentList:
            l = int(l)
            payment = Payment.objects.get(pk=l)
            payment.delete()
        messages.success(request, f'{len(paymentList)} תשלומים נמחקו בהצלחה')
        return redirect(fallback)


@login_required
def payment_send_invoice(request, pk):
    if request.method == "POST":
        fallback = request.POST["fallback"]
        payment = Payment.objects.get(pk=pk)
        payment.status = "billed"
        payment.invoice_date = timezone.now().date()
        payment.save()
        messages.success(request, 'חשבונית נשלחה בהצלחה', extra_tags=payment.name)
        if fallback == 'customer-detail':
            base_url = reverse('customer-detail', args=(payment.project.customer.id,))
            query_string = urlencode({'section': 'payments'})
            url = f'{base_url}?{query_string}'
            return redirect(url)
        elif fallback == 'project-detail':
            base_url = reverse('project-detail', args=(payment.project.id,))
            query_string = urlencode({'section': 'payments'})
            url = f'{base_url}?{query_string}'
            return redirect(url)
        elif fallback == 'payment-list':
            return redirect(reverse('payment-list'))

@login_required
def payment_send_recipt(request, pk):
    if request.method == "POST":
        fallback = request.POST["fallback"]
        payment = Payment.objects.get(pk=pk)
        payment.status = "paid"
        payment.recipt_date = timezone.now().date()
        payment.save()
        messages.success(request, 'קבלה נשלחה בהצלחה', extra_tags=payment.name)
        if fallback == 'customer-detail':
            base_url = reverse('customer-detail', args=(payment.project.customer.id,))
            query_string = urlencode({'section': 'payments'})
            url = f'{base_url}?{query_string}'
            return redirect(url)
        elif fallback == 'project-detail':
            base_url = reverse('project-detail', args=(payment.project.id,))
            query_string = urlencode({'section': 'payments'})
            url = f'{base_url}?{query_string}'
            return redirect(url)
        elif fallback == 'payment-list':
            return redirect(reverse('payment-list'))

    
