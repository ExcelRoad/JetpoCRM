from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Service, Task, Timesheet
from projects.models import Project, ProjectBudget


def get_service_info(request, pk):

    service = Service.objects.get(pk=pk)
    qty = service.default_qty
    price = service.default_price
    info = {
        'qty': qty,
        'price': price,
    }
    return JsonResponse(info)


def task_create_update(request, pk):
    taskTitle = request.POST['taskTitle']
    taskDescription = request.POST['taskDescription']
    projectId = request.POST['project']
    taskUrgency = request.POST['taskUrgency']
    project = Project.objects.get(pk=projectId)
    if pk==0 or pk=="0":
        task = Task.objects.create(
            title = taskTitle,
            description = taskDescription,
            content_object = project,
            urgency = taskUrgency,
            is_completed = False
        )
    else:
        task = Task.objects.get(pk=pk)
        task.title = taskTitle
        task.description = taskDescription
        task.urgency = taskUrgency
        task.save()
    return redirect('project-detail', project.id)


def task_complete(request, pk):
    if request.method == 'POST':
        task = Task.objects.get(pk=pk)
        task.is_completed = True
        task.save()
        return redirect('project-detail', task.object_id)

def task_delete(request, pk):
    if request.method == 'POST':
        task = Task.objects.get(pk=pk)
        task.delete()
        return redirect('project-detail', task.object_id)
    

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
        else:
            timesheet = Timesheet.objects.get(pk=timesheetId)
            timesheet.date = ts_date
            timesheet.descriptiokn = ts_description
            timesheet.hours = ts_hours
            timesheet.save()
        return redirect('project-detail', task.object_id )
    
def timesheet_delete(request, pk):
    if request.method == 'POST':
        timesheet = Timesheet.objects.get(pk=pk)
        timesheet.delete()
        return redirect('project-detail', timesheet.task.object_id)

