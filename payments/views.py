from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from .models import Payment
from projects.models import Project

def payment_edit(request, pk, main = False):
    if request.method == "POST":
        payQty = request.POST['paymentQty']
        payPrice = request.POST['paymentPrice']
        payName = request.POST['paymentName']
        projectId = request.POST['project']
        project = Project.objects.get(pk = int(projectId))
        if pk != 0 and pk != '0':
            payment = Payment.objects.get(pk=pk)
            payment.qty = payQty
            payment.price = payPrice
            payment.name = payName
            payment.save()
        else:
            payment = Payment.objects.create(
                name = payName,
                service = project.service,
                project = project,
                qty = payQty,
                price = payPrice,
                status = 'draft'
            )
        if main:
            url = reverse('payment-list')
        else:
            base_url = reverse('project-detail', args=(payment.project.id,))
            query_string = urlencode({'section': 'payments'})
            url = f'{base_url}?{query_string}'
        return redirect(url)

def payment_delete(request, pk, main = False):
    payment = Payment.objects.get(pk=pk)
    payment.delete()
    if main:
        url = reverse('payment-list')
    else:
        base_url = reverse('project-detail', args=(payment.project.id,))
        query_string = urlencode({'section': 'payments'})
        url = f'{base_url}?{query_string}'
    return redirect(url)

def payment_list(request):
    payments = Payment.objects.all()
    context = {
        'payments': payments,
    }
    return render(request, 'payments/payment-list.html', context)

def payment_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        paymentList = request.POST['paymentList']
        paymentList = paymentList.split(',')
        for l in paymentList:
            l = int(l)
            payment = Payment.objects.get(pk=l)
            payment.delete()
        return redirect(fallback)

    
