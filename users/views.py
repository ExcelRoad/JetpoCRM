from django.shortcuts import render
from leads.models import Lead, LeadSource
from quotes.models import Quote
from payments.models import Payment
from projects.models import Project
from django.contrib.auth import login as login_func
from .forms import LoginForm, RegisterForm
from django.shortcuts import redirect
from django.contrib.auth import logout as logout_func
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

@login_required
def homePage(request):
    # Leads KPI
    open_leads = Lead.objects.filter(status__in=['new','follow', 'quote'])
    this_week_leads = Lead.objects.filter(created_at__gte=timezone.now() - timedelta(weeks=1))
    this_month_leads = Lead.objects.filter(created_at__month=timezone.now().month)
    last_month_leads = Lead.objects.filter(created_at__month=timezone.now().month - 1)
    last_month_leads_change = this_month_leads.count() - last_month_leads.count()
    if last_month_leads.count() > 0:
        mom_lead_change_percent = last_month_leads_change / last_month_leads.count() * 100
    else:
        mom_lead_change_percent = 100
    # Quotes KPI
    open_quotes = Quote.objects.filter(status__in=['draft', 'sent'])
    open_quotes_value = 0
    for quote in open_quotes:
        open_quotes_value += quote.total_price
    old_open_quotes = open_quotes.filter(created_at__gte=timezone.now() - timedelta(weeks=3))
    if open_quotes.count() > 0:
        old_open_quotes_percent = old_open_quotes.count() / open_quotes.count() * 100
    else:
        old_open_quotes_percent = 0
    # Payments KPI
    open_payments = Payment.objects.filter(status__in=['draft', 'billed'])
    open_payments_value = 0
    for payment in open_payments:
        open_payments_value += payment.total_price
    draft_payments = open_payments.filter(status='draft')
    billed_payments = open_payments.filter(status='billed')
    # Projects
    open_projects = Project.objects.filter(status__in=['open', 'onHold'])
    # Lead Source
    lead_sources = LeadSource.objects.all()
    # Lead Status
    leadStatus = Lead.LEAD_STATUSES
    leadStatusCount = []
    for i, status in enumerate(leadStatus):
        statusMap = {}
        statusMap['name'] = status[0]
        statusMap['display'] = status[1]
        statusMap['count'] = Lead.objects.filter(status=status[0]).count()
        leadStatusCount.append(statusMap)
    # Lead Create Date
    leadCreatelist = [
        {
            'name': 'היום',
            'count': Lead.objects.filter(created_at=timezone.now()).count()
        },
        {
            'name': 'שבוע שעבר',
            'count': this_week_leads.count()
        },
        {
            'name': 'חודש שעבר',
            'count': Lead.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()
        },
        {
            'name': 'שנה שעברה',
            'count': Lead.objects.filter(created_at__gte=timezone.now() - timedelta(days=365)).count()
        }
    ]

    context = {
        'open_leads': open_leads,
        'this_week_leads': this_week_leads,
        'mom_lead_change_percent': mom_lead_change_percent,
        'open_quotes': open_quotes,
        'open_quotes_value': open_quotes_value,
        'old_open_quotes_percent': old_open_quotes_percent,
        'open_payments': open_payments,
        'open_payments_value': open_payments_value,
        'draft_payments': draft_payments,
        'billed_payments': billed_payments,
        'open_projects': open_projects,
        'leadSources': lead_sources,
        'leadStatusCount': leadStatusCount,
        'leadCreatelist': leadCreatelist
    }
    return render(request, 'base/home.html', context)

def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login_func(request, user)
            return redirect('homePage') # Redirect to homePage which is the name of the URL for home
    else:
        form = LoginForm()
    return render(request, 'base/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login_func(request, user)
            return redirect('homePage')
    else:
        form = RegisterForm()
    return render(request, 'base/register.html', {'form': form})


@login_required
def logout(request):
    logout_func(request)
    return redirect('login')
