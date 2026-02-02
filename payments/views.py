from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from .models import Payment
from django.contrib import messages
from projects.models import Project
from django.contrib.auth.decorators import login_required

@login_required
def payment_edit(request, pk, main = False):
    if request.method == "POST":
        payQty = request.POST['paymentQty']
        payPrice = request.POST['paymentPrice']
        payName = request.POST['paymentName']
        projectId = request.POST['project']
        if pk != 0 and pk != '0':
            payment = Payment.objects.get(pk=pk)
            payment.qty = payQty
            payment.price = payPrice
            payment.name = payName
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
                status = 'draft'
            )
            messages.success(request, 'תשלום נוצר בהצלחה', extra_tags=payment.name)
        if main:
            url = reverse('payment-list')
        else:
            base_url = reverse('project-detail', args=(payment.project.id,))
            query_string = urlencode({'section': 'payments'})
            url = f'{base_url}?{query_string}'
        return redirect(url)

@login_required
def payment_delete(request, pk, main = False):
    payment = Payment.objects.get(pk=pk)
    payment.delete()
    messages.success(request, 'תשלום נמחק בהצלחה', extra_tags=payment.name)
    if main:
        url = reverse('payment-list')
    else:
        base_url = reverse('project-detail', args=(payment.project.id,))
        query_string = urlencode({'section': 'payments'})
        url = f'{base_url}?{query_string}'
    return redirect(url)

@login_required
def payment_list(request):
    payments = Payment.objects.all()
    context = {
        'payments': payments,
    }
    return render(request, 'payments/payment-list.html', context)

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

    
