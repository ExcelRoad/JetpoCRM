from django.shortcuts import render
from leads.models import Lead, LeadSource
from customers.models import Customer
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

    # Income Chart Data
        # Calculate start date (11 months ago from current month start) to cover 12 months including current
    today = timezone.localtime(timezone.now()).date()
    # If today is 2023-10-15, start_date should be 2022-11-01
    start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1) # Go back to start of prev month, then go back 11 more months?
    # Simpler approach: go back 365 days
    start_date = today - timedelta(days=365)
    
    from django.db.models import Sum, F
    from django.db.models.functions import TruncMonth

    monthly_income = (
        Payment.objects
        .filter(status='paid', recipt_date__gte=start_date)
        .annotate(month=TruncMonth('recipt_date'))
        .values('month')
        .annotate(total_income=Sum(F('qty') * F('price')))
        .order_by('month')
    )

    # Process data to ensure all 12 months are present and formatted for Chart.js
    income_labels = []
    income_data_list = []
    
    # Generate list of last 12 months
    current_month_start = today.replace(day=1)
    months_list = []
    for i in range(12):
        d = current_month_start
        month_ago = i
        year = d.year
        month = d.month - month_ago
        while month <= 0:
            month += 12
            year -= 1
        months_list.append(d.replace(year=year, month=month))
        
    hebrew_months = {
        1: 'ינואר',
        2: 'פברואר',
        3: 'מרץ',
        4: 'אפריל',
        5: 'מאי',
        6: 'יוני',
        7: 'יולי',
        8: 'אוגוסט',
        9: 'ספטמבר',
        10: 'אוקטובר',
        11: 'נובמבר',
        12: 'דצמבר'
    }

    for m_date in months_list:
        # Label format: "HebrewMonth Year" e.g., "אוקטובר 2023"
        month_name = hebrew_months[m_date.month]
        label = f"{month_name} {m_date.year}"
        income_labels.append(label)
        
        # Find matching data
        total = 0
        for entry in monthly_income:
            if entry['month'].year == m_date.year and entry['month'].month == m_date.month:
                total = entry['total_income']
                break
        income_data_list.append(float(total))
    
    # Customer Ranking by income with the ranking number and only 4 top customers
    customer_ranking_list = []
    all_customers = Customer.objects.all()
    for customer in all_customers:
        customer_ranking_list.append({
            'name': customer.name,
            'income': customer.total_income,
            'logo': customer.logo,
            'customer_id': customer.id,
        })
    customer_ranking_list = sorted(customer_ranking_list, key=lambda x: x['income'], reverse=True)
    customer_ranking_list = customer_ranking_list[:4]
    for i, customer in enumerate(customer_ranking_list):
        customer['rank'] = i + 1


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
        'leadCreatelist': leadCreatelist,
        'income_labels': income_labels,
        'income_data': income_data_list,
        'customer_ranking_list': customer_ranking_list,
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
