from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode
from activities.models import Note, Task
from .models import Project, ProjectBudget
from customers.models import Customer
from .forms import ProjectForm
from payments.models import Payment
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.utils import export_to_excel
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from core.import_utils import generate_csv_template, parse_csv_row_count, get_csv_data
from activities.models import Service

@login_required
def project_import_template(request):
    return generate_csv_template(Project)

@csrf_exempt
@login_required
def project_import_preview(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        row_count = parse_csv_row_count(file.read())
        return JsonResponse({'success': True, 'row_count': row_count})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@login_required
def project_import_confirm(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        data = get_csv_data(file.read())
        
        created_count = 0
        updated_count = 0
        failed_count = 0
        
        for row in data:
            try:
                # Normalize keys to lowercase for flexible matching
                row_lower = {str(k).lower().strip(): v for k, v in row.items()}
                
                def get_val(aliases):
                    for alias in aliases:
                        if alias.lower() in row_lower:
                            return row_lower[alias.lower()]
                    return None

                def map_choice(val, choices):
                    if not val: return None
                    val = str(val).strip().lower()
                    for key, label in choices:
                        if val == key.lower() or val == label.lower():
                            return key
                    return val

                # Handle Customer relationship
                customer = None
                customer_name = get_val(['customer', 'company', 'חברה', 'לקוח'])
                if customer_name:
                    customer = Customer.objects.filter(name__icontains=customer_name.strip()).first()
                
                # Handle Service relationship
                service = None
                service_name = get_val(['service', 'שירות', 'סוג שירות'])
                if service_name:
                    service = Service.objects.filter(name__icontains=service_name.strip()).first()
                
                status_val = get_val(['status', 'סטטוס'])
                mapped_status = map_choice(status_val, Project.STATUSES) or 'open'

                if customer:
                    Project.objects.create(
                        name=get_val(['name', 'שם', 'פרויקט', 'שם פרויקט']) or 'Imported Project',
                        status=mapped_status,
                        customer=customer,
                        service=service
                    )
                    created_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Error importing project row: {e}")
                failed_count += 1
                
        return JsonResponse({
            'success': True,
            'created': created_count,
            'updated': updated_count,
            'failed': failed_count
        })
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
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
            messages.success(request, 'פרויקט נוצר בהצלחה', extra_tags=project.name)
            return redirect('project-detail', project.id)
        else:
            messages.error(request, 'שגיאה ביצירת הפרויקט')
    context = {
        'form': form,
        'form_header': 'יצירת פרויקט',
    }
    return render(request, 'projects/project-form.html', context)


@login_required
def project_edit(request, pk, fallback):
    project = Project.objects.get(pk=pk)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            messages.success(request, 'פרויקט עודכן בהצלחה', extra_tags=project.name)
            if fallback == "customer-detail":
                return redirect('customer-detail', project.customer.id)
            elif fallback == 'project-detail':
                return redirect('project-detail', project.id)
            else:
                return redirect(fallback)
        else:
            messages.error(request, 'שגיאה בשמירת הפרויקט')
    context = {
        'form': form,
        'form_header': 'עריכת פרויקט',
        'project': project
    }
    return render(request, 'projects/project-form.html', context)


@login_required
def project_delete(request, pk):
    if request.method == "POST":
        fallback = request.POST['fallback']
        project = Project.objects.get(pk=pk)
        project.delete()
        messages.success(request, 'פרויקט נמחק בהצלחה', extra_tags=project.name)
        if "detail" in fallback:
            return redirect(fallback, project.customer.id)
        else:
            return redirect(fallback)
        
@login_required
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
        'today': timezone.now().date(),
    }
    return render(request, 'projects/project-detail.html', context)


@login_required
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

@login_required
def project_delete_note(request, noteid):
    note = Note.objects.get(pk=noteid)
    project = Project.objects.get(pk=note.object_id)
    note.delete()
    messages.success(request, 'הערה נמחקה בהצלחה', extra_tags=project.name)
    base_url = reverse('project-detail', args=(project.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

@login_required
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

@login_required
def project_list(request):
    projects = Project.objects.all()

    context = {
        'projects': projects,
    }
    return render(request, 'projects/project-list.html', context)


@login_required
def project_export(request):
    if request.method == "POST":
        projectList = request.POST.get('projectList')
        if projectList:
            project_ids = [int(id) for id in projectList.split(',')]
            projects = Project.objects.filter(id__in=project_ids)
            return export_to_excel(projects, filename_prefix="projects_export")
    return redirect('project-list')


@login_required
def project_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        projectList = request.POST['projectList']
        projectList = projectList.split(',')
        for l in projectList:
            l = int(l)
            project = Project.objects.get(pk=l)
            project.delete()
        messages.success(request, f'{len(projectList)} פרויקטים נמחקו בהצלחה')
        return redirect(fallback)
    

@login_required
def project_budget_activate(request, pk):
    budget = ProjectBudget.objects.get(pk=pk)
    allBudgets = ProjectBudget.objects.filter(project = budget.project).update(is_active = False)
    budget.is_active = True
    budget.save()
    base_url = reverse('project-detail', args=(budget.project.id,))
    query_string = urlencode({'section': 'budgets'})
    url = f'{base_url}?{query_string}'
    return redirect(url)


@login_required
def budget_delete(request, pk):
    budget = ProjectBudget.objects.get(pk=pk)
    budget.delete()
    messages.success(request, 'תקציב פרויקט נמחק בהצלחה', extra_tags=budget.project.name)
    base_url = reverse('project-detail', args=(budget.project.id,))
    query_string = urlencode({'section': 'budgets'})
    url = f'{base_url}?{query_string}'
    return redirect(url)


@login_required
def budget_create_update(request, pk):
    if request.method == 'POST':
        name = request.POST['budgetName']
        qty = request.POST['budgetQty']
        price = request.POST['budgetPrice']
        projectId = request.POST['project']
        project = Project.objects.get(pk=projectId)
        if pk == 0 or pk == '0':
            # make other budgets be non active
            otherBudgets = ProjectBudget.objects.filter(project = project).update(is_active = False)
            budget = ProjectBudget.objects.create(
                name = name,
                qty = qty,
                price = price,
                project = project,
                is_active = True
            )
            messages.success(request, 'תקציב פרויקט נוצר בהצלחה', extra_tags=budget.project.name)
        else:
            budget = ProjectBudget.objects.get(pk=pk)
            budget.name = name
            budget.qty = qty
            budget.price = price
            budget.save()
            messages.success(request, 'תקציב פרויקט עודכן בהצלחה', extra_tags=budget.project.name)
    base_url = reverse('project-detail', args=(budget.project.id,))
    query_string = urlencode({'section': 'budgets'})
    url = f'{base_url}?{query_string}'
    return redirect(url)


@login_required
def budget_add(request, pk):
    from decimal import Decimal
    if request.method == 'POST':
        qty = request.POST['budgetQty']
        budget = ProjectBudget.objects.get(pk=pk)
        budget.qty += Decimal(qty)
        budget.save()
        # Create payment for the additional budget
        payment = Payment.objects.create(
            name = f'תוספת תקציב ל{budget.name}',
            service = budget.project.service,
            qty = qty,
            price = budget.price,
            project = budget.project,
            status = 'draft'
        )
        messages.success(request, 'תקציב פרויקט עודכן בהצלחה', extra_tags=budget.project.name)
        base_url = reverse('project-detail', args=(budget.project.id,))
        query_string = urlencode({'section': 'budgets'})
        url = f'{base_url}?{query_string}'
        return redirect(url)

