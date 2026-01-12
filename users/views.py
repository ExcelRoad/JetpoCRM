from django.shortcuts import render
from leads.models import Lead


def homePage(request):
    return render(request, 'base/home.html')
