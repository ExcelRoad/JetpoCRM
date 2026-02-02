from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .models import Service, Task, Timesheet, Meeting
from projects.models import Project, ProjectBudget
from leads.models import LeadSource
from alerts.models import AlertSettings, AlertType
from django.contrib import messages
from connections.models import Workdrive, Sumit
from django.contrib.auth.decorators import login_required


@login_required
def settings_page(request):
    lead_sources = LeadSource.objects.all()
    services = Service.objects.all()
    lead_alert_type, created = AlertType.objects.get_or_create(
        name = 'Leads',
        slug = 'leads'
    )
    lead_alert_settings, created = AlertSettings.objects.get_or_create(
        user = request.user,
        alert_type = lead_alert_type
    )
    workdrive_settings = Workdrive.objects.first()
    if workdrive_settings is None:
        workdrive_settings = Workdrive.objects.create(
            client_id = '',
            client_secret = '',
            is_connected = False
        )
    sumit_settings = Sumit.objects.first()
    if sumit_settings is None:
        sumit_settings = Sumit.objects.create(
            company_id = '',
            api_key = '',
            customer_folder_id = '',
            is_connected = False
        )
    context = {
        'lead_sources': lead_sources,
        'lead_alert_settings' : lead_alert_settings,
        'workdrive': workdrive_settings,
        'sumit': sumit_settings,
        'services': services
    }
    return render(request, 'base/settings-page.html', context)

@login_required
def profile_page(request):
    base_url = reverse('settings')
    query_string = urlencode({'section': 'profile'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

@login_required
def get_service_info(request, pk):

    service = Service.objects.get(pk=pk)
    qty = service.default_qty
    price = service.default_price
    info = {
        'qty': qty,
        'price': price,
    }
    return JsonResponse(info)


@login_required
def task_create_update(request, pk):
    taskTitle = request.POST['taskTitle']
    taskDescription = request.POST['taskDescription']
    projectId = request.POST['project']
    taskUrgency = request.POST['taskUrgency']
    if pk==0 or pk=="0" and projectId != "":
        project = Project.objects.get(pk=projectId)
        task = Task.objects.create(
            title = taskTitle,
            description = taskDescription,
            content_object = project,
            urgency = taskUrgency,
            is_completed = False
        )
        messages.success(request, 'המשימה נוצרה בהצלחה', extra_tags=task.title)
    else:
        task = Task.objects.get(pk=pk)
        task.title = taskTitle
        task.description = taskDescription
        task.urgency = taskUrgency
        task.save()
        messages.success(request, 'המשימה עודכנה בהצלחה', extra_tags=task.title)
    if projectId != "":
        base_url = reverse('project-detail', args=(task.object_id,))
        query_string = urlencode({'section': 'tasks'})
        url = f'{base_url}?{query_string}'
        return redirect(url)
    else:
        return redirect('task-list')


@login_required
def task_complete(request, pk, main=False):
    if request.method == 'POST':
        task = Task.objects.get(pk=pk)
        task.is_completed = True
        task.save()
        messages.success(request, 'המשימה הושלמה בהצלחה', extra_tags=task.title)
        if main == "False":
            base_url = reverse('project-detail', args=(task.object_id,))
            query_string = urlencode({'section': 'tasks'})
            url = f'{base_url}?{query_string}'
            return redirect(url)
        else:
            return redirect('task-list')

@login_required
def task_delete(request, pk):
    if request.method == 'POST':
        fallback = request.POST['fallback']
        task = Task.objects.get(pk=pk)
        task.delete()
        messages.success(request, 'המשימה נמחקה בהצלחה', extra_tags=task.title)
        if fallback == "task-list":
            return redirect('task-list')
        base_url = reverse('project-detail', args=(task.object_id,))
        query_string = urlencode({'section': 'tasks'})
        url = f'{base_url}?{query_string}'
        return redirect(url)
    

@login_required
def timesheet_create_update(request, pk):
    if request.method == 'POST':
        timesheetId = request.POST['timesheet']
        task = Task.objects.get(pk=pk)
        budget = ProjectBudget.objects.filter(project = task.object_id, is_active=True).first()
        ts_date = request.POST['timesheetDate']
        ts_hours = request.POST['timesheetHours']
        ts_description = request.POST['timesheetDescription']
        if timesheetId == 0 or timesheetId == '0':
            timesheet = Timesheet.objects.create(
                date = ts_date,
                hours = ts_hours,
                description = ts_description,
                is_billed = False,
                task = task,
                budget = budget
            )
            messages.success(request, 'דיווח שעות נוצר בהצלחה', extra_tags=timesheet)
        else:
            timesheet = Timesheet.objects.get(pk=timesheetId)
            timesheet.date = ts_date
            timesheet.descriptiokn = ts_description
            timesheet.hours = ts_hours
            timesheet.save()
            messages.success(request, 'דיווח שעות עודכן בהצלחה', extra_tags=timesheet)
        base_url = reverse('project-detail', args=(task.object_id,))
        query_string = urlencode({'section': 'timesheets'})
        url = f'{base_url}?{query_string}'
        return redirect(url)
    
@login_required
def timesheet_delete(request, pk):
    if request.method == 'POST':
        timesheet = Timesheet.objects.get(pk=pk)
        timesheet.delete()
        messages.success(request, 'דיווח שעות נמחק בהצלחה', extra_tags=timesheet)
        base_url = reverse('project-detail', args=(timesheet.task.object_id,))
        query_string = urlencode({'section': 'timesheets'})
        url = f'{base_url}?{query_string}'
        return redirect(url)


@login_required
def task_list(request):
    tasks = Task.objects.all()
    context = {
        'tasks': tasks,
    }
    return render(request, 'projects/task-list.html', context)


@login_required
def task_mass_complete(request):
    if request.method == 'POST':
        tasks = request.POST['tasks'].split(',')
        for task in tasks:
            task = Task.objects.get(pk=task)
            task.is_completed = True
            task.save()
        messages.success(request, f'{tasks.count()} משימות הושלמו בהצלחה')
        return redirect('task-list')

@login_required
def task_uncomplete(request, pk):
    if request.method == 'POST':
        fallback = request.POST['fallback']
        task = Task.objects.get(pk=pk)
        task.is_completed = False
        task.save()
        messages.success(request, 'המשימה נפתחה חזרה', extra_tags=task.title)
        if fallback == "task-list":
            
            return redirect('task-list')
        base_url = reverse('project-detail', args=(task.object_id,))
        query_string = urlencode({'section': 'tasks'})
        url = f'{base_url}?{query_string}'
        return redirect(url)

@login_required
def leadsource_save(request):
    if request.method == 'POST':
        leadsourceId = request.POST['leadsource']
        leadsourceName = request.POST['leadsourceName']
        if leadsourceId == '0' or leadsourceId == 0:
            leadsource = LeadSource.objects.create(
                name = leadsourceName
            )
            messages.success(request, 'מקור ליד נוצר בהצלחה', extra_tags=leadsource.name)
        else:
            leadsource = LeadSource.objects.get(pk=leadsourceId)
            leadsource.name = leadsourceName
            leadsource.save()
            messages.success(request, 'מקור ליד עודכן בהצלחה', extra_tags=leadsource.name)
        base_url = reverse('settings')
        query_string = urlencode({'section': 'leads', 'subsection': '1'})
        url = f'{base_url}?{query_string}'
        return redirect(url)

@login_required
def leadsource_delete(request, pk):
    if request.method == 'POST':
        leadsource = LeadSource.objects.get(pk=pk)
        leadsource.delete()
        messages.success(request, 'מקור ליד נמחק בהצלחה', extra_tags=leadsource.name)
        base_url = reverse('settings')
        query_string = urlencode({'section': 'leads', 'subsection': '1'})
        url = f'{base_url}?{query_string}'
        return redirect(url)


@login_required
def meeting_delete(request, pk):
    if request.method == 'POST':
        fallback = request.POST['fallback']
        meeting = Meeting.objects.get(pk=pk)
        meeting.delete()
        messages.success(request, 'פגישה נמחקה בהצלחה', extra_tags=meeting.title)
        base_url = reverse(fallback, args=(meeting.object_id,))
        query_string = urlencode({'section': 'activities'})
        url = f'{base_url}?{query_string}'
        return redirect(url)

@login_required
def meeting_create_update(request, pk=None):
    if request.method == 'POST':
        fallback = request.POST['fallback']
        meetingTitle = request.POST['meetingTitle']
        meetingDescription = request.POST['meetingDescription']
        meetingDate = request.POST['meetingDate']
        meetingStartTime = request.POST['meetingStartTime']
        meetingDuration = request.POST['meetingDuration']
        if request.POST.get('meetingIsOnline') == 'on':
            meetingIsOnline = True
        else:
            meetingIsOnline = False
        meetingLocation = request.POST['meetingLocation']
        content_type = request.POST['contentType']
        object_id = request.POST['objectId']
        if pk == '0' or pk == 0:
            meeting = Meeting.objects.create(
                title = meetingTitle,
                description = meetingDescription,
                date = meetingDate,
                start_time = meetingStartTime,
                duration = meetingDuration,
                is_online = meetingIsOnline,
                location = meetingLocation,
                object_id = object_id,
                content_type = ContentType.objects.get(model=content_type),
            )
            messages.success(request, 'פגישה נוצרה בהצלחה', extra_tags=meeting.title)
        else:
            meeting = Meeting.objects.get(pk=pk)
            meeting.title = meetingTitle
            meeting.description = meetingDescription
            meeting.date = meetingDate
            meeting.start_time = meetingStartTime
            meeting.duration = meetingDuration
            meeting.is_online = meetingIsOnline
            meeting.location = meetingLocation
            meeting.save()
            messages.success(request, 'פגישה עודכנה בהצלחה', extra_tags=meeting.title)
        base_url = reverse(fallback, args=(object_id,))
        query_string = urlencode({'section': 'activities'})
        url = f'{base_url}?{query_string}'
        return redirect(url)

@login_required
def meeting_complete(request, pk):
    if request.method == 'POST':
        fallback = request.POST['fallback']
        meeting = Meeting.objects.get(pk=pk)
        meeting.status = 'completed'
        meeting.save()
        messages.success(request, 'פגישה הושלמה בהצלחה', extra_tags=meeting.title)
        base_url = reverse(fallback, args=(meeting.object_id,))
        query_string = urlencode({'section': 'activities'})
        url = f'{base_url}?{query_string}'
        return redirect(url)


@login_required
def service_delete(request, pk):
    if request.method == 'POST':
        service = Service.objects.get(pk=pk)
        service.delete()
        messages.success(request, 'שירות נמחק בהצלחה', extra_tags=service.name)
        base_url = reverse('settings')
        query_string = urlencode({'section': 'general', 'subsection': '1'})
        url = f'{base_url}?{query_string}'
        return redirect(url)

@login_required
def service_save(request):
    if request.method == 'POST':
        serviceId = request.POST['service']
        serviceName = request.POST['serviceName']
        if serviceId == '0' or serviceId == 0:
            service = Service.objects.create(
                name = serviceName,
                budget_type = request.POST['serviceBudgetType'],
                default_qty = request.POST['serviceQty'],
                default_price = request.POST['servicePrice'],
                is_subscription = request.POST.get('service_is_subscription') == 'on',
            )
            messages.success(request, 'שירות נוצר בהצלחה', extra_tags=service.name)
        else:
            service = Service.objects.get(pk=serviceId)
            service.name = serviceName
            service.budget_type = request.POST['serviceBudgetType']
            service.default_qty = request.POST['serviceQty']
            service.default_price = request.POST['servicePrice']
            service.is_subscription = request.POST.get('service_is_subscription') == 'on'
            service.save()
            messages.success(request, 'שירות עודכן בהצלחה', extra_tags=service.name)
        base_url = reverse('settings')
        query_string = urlencode({'section': 'general', 'subsection': '1'})
        url = f'{base_url}?{query_string}'
        return redirect(url)
