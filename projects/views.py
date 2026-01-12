from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from activities.models import Note, Task
from .models import Project, ProjectBudget
from customers.models import Customer
from .forms import ProjectForm


def project_create(request, customerId = None):
    if customerId:
        customer = Customer.objects.get(pk=customerId)
        form = ProjectForm(initial={
            'customer': customer
        })
    else:
        form = ProjectForm()
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save()
            return redirect('project-detail', project.id)
    context = {
        'form': form,
        'form_header': 'יצירת פרויקט',
    }
    return render(request, 'projects/project-form.html', context)


def project_edit(request, pk, fallback):
    project = Project.objects.get(pk=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            if fallback == "customer-detail":
                return redirect('customer-detail', project.customer.id)
            elif fallback == 'project-detail':
                return redirect('project-detail', project.id)
            else:
                return redirect(fallback)
    context = {
        'form': form,
        'form_header': 'עריכת פרויקט',
        'project': project
    }
    return render(request, 'projects/project-form.html', context)


def project_delete(request, pk):
    if request.method == "POST":
        fallback = request.POST['fallback']
        project = Project.objects.get(pk=pk)
        project.delete()
        if "detail" in fallback:
            return redirect(fallback, project.customer.id)
        else:
            return redirect(fallback)
        
def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    tagged_note = Note.objects.filter(
        content_type__model = 'project',
        object_id = project.id,
        tagged = True
    ).first()
    context = {
        'project': project,
        'tagged_note': tagged_note,
    }
    return render(request, 'projects/project-detail.html', context)


def project_submit_note(request, pk):
    project = Project.objects.get(pk = pk)
    note = Note.objects.create(
        text = request.POST['note'],
        content_object = project
    )
    base_url = reverse('project-detail', args=(pk,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def project_delete_note(request, noteid):
    note = Note.objects.get(pk=noteid)
    project = Project.objects.get(pk=note.object_id)
    note.delete()
    base_url = reverse('project-detail', args=(project.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def project_tag_note(request, noteid):
    # remove tag from all Notes for this Lead
    note = Note.objects.get(pk=noteid)
    if note.tagged:
        note.tagged = False
    else:
        all_notes = Note.objects.filter(object_id=note.content_object.id).update(tagged=False)
        note.tagged = True
    note.save()
    base_url = reverse('project-detail', args=(note.content_object.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

def project_list(request):
    projects = Project.objects.all()

    context = {
        'projects': projects,
    }
    return render(request, 'projects/project-list.html', context)


def project_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        projectList = request.POST['projectList']
        projectList = projectList.split(',')
        for l in projectList:
            l = int(l)
            project = Project.objects.get(pk=l)
            project.delete()
        return redirect(fallback)
    

def project_budget_activate(request, pk):
    budget = ProjectBudget.objects.get(pk=pk)
    budget.is_active = True
    budget.save()
    return redirect('project-detail', budget.project.id)


def budget_delete(request, pk):
    budget = ProjectBudget.objects.get(pk=pk)
    budget.delete()
    return redirect('project-detail', budget.project.id)


def budget_create_update(request, pk):
    if request.method == 'POST':
        name = request.POST['budgetName']
        qty = request.POST['budgetQty']
        price = request.POST['budgetPrice']
        projectId = request.POST['project']
        project = Project.objects.get(pk=projectId)
        if pk == 0 or pk == '0':
            budget = ProjectBudget.objects.create(
                name = name,
                qty = qty,
                price = price,
                project = project
            )
        else:
            budget = ProjectBudget.objects.get(pk=pk)
            budget.name = name
            budget.qty = qty
            budget.price = price
            budget.save()
    return redirect('project-detail', project.id)


def budget_add(request, pk):
    from decimal import Decimal
    if request.method == 'POST':
        qty = request.POST['budgetQty']
        budget = ProjectBudget.objects.get(pk=pk)
        budget.qty += Decimal(qty)
        budget.save()
        return redirect('project-detail', budget.project.id)

