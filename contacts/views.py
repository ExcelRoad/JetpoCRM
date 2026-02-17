from django.shortcuts import render, redirect
from .models import Contact
from .forms import ContactForm
from django.urls import reverse
from urllib.parse import urlencode
from activities.models import Note
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.utils import export_to_excel
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from core.import_utils import generate_csv_template, parse_csv_row_count, get_csv_data
from customers.models import Customer

@login_required
def contact_import_template(request):
    return generate_csv_template(Contact)

@csrf_exempt
@login_required
def contact_import_preview(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        row_count = parse_csv_row_count(file.read())
        return JsonResponse({'success': True, 'row_count': row_count})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@login_required
def contact_import_confirm(request):
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

                # Handle Customer foreign key with aliases
                customer = None
                customer_name = get_val(['customer', 'company', 'חברה', 'לקוח', 'שם לקוח', 'שם חברה'])
                if customer_name:
                    customer = Customer.objects.filter(name__icontains=customer_name.strip()).first()
                
                email = get_val(['email', 'אימייל', 'דואל', 'דואר אלקטרוני']) or ''
                email = str(email).strip()
                
                phone = get_val(['phone', 'טלפון', 'נייד', 'סלולרי']) or ''
                phone = str(phone).strip()
                
                first_name = get_val(['first_name', 'שם פרטי', 'שם']) or ''
                first_name = str(first_name).strip()
                
                last_name = get_val(['last_name', 'שם משפחה']) or ''
                last_name = str(last_name).strip()

                if not first_name:
                    failed_count += 1
                    continue

                # Try matching existing contact for upsert
                contact = None
                if email:
                    contact = Contact.objects.filter(email=email).first()
                if not contact and phone:
                    contact = Contact.objects.filter(phone=phone).first()
                
                contact_type_val = get_val(['contact_type', 'סוג איש קשר', 'סוג'])
                mapped_type = map_choice(contact_type_val, Contact.CONTACT_TYPES) or 'normal'

                defaults = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'role': get_val(['role', 'תפקיד']) or '',
                    'contact_type': mapped_type,
                    'customer': customer
                }

                if contact:
                    for key, value in defaults.items():
                        setattr(contact, key, value)
                    contact.save()
                    updated_count += 1
                else:
                    Contact.objects.create(**defaults)
                    created_count += 1
                    
            except Exception as e:
                print(f"Error importing contact row: {e}")
                failed_count += 1
                
        return JsonResponse({
            'success': True, 
            'created': created_count, 
            'updated': updated_count, 
            'failed': failed_count
        })
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def contact_list(request):
    contacts = Contact.objects.all()
    context = {
        'contacts': contacts,
    }
    return render(request, 'contacts/contact-list.html', context)


@login_required
def contact_create(request, pk=None):
    if pk == None:
        form = ContactForm()
    else:
        form = ContactForm(initial={'customer': pk})
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, 'איש הקשר נוצר בהצלחה', extra_tags=contact.full_name)
            return redirect('contact-detail', contact.id)
        else:
            messages.error(request, 'ישנה בעיה בשמירת איש הקשר', extra_tags=contact.full_name)
    context = {
        'form': form,
        'form_header': 'יצירת איש קשר',
    }
    return render(request, 'contacts/contact-form.html', context)


@login_required
def contact_edit(request, pk, fallback):
    contact = Contact.objects.get(pk=pk)
    form = ContactForm(instance=contact)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'איש הקשר עודכן בהצלחה', extra_tags=contact.full_name)
            if fallback == "contact-detail":
                return redirect('contact-detail', contact.id)
            elif fallback == 'customer-detail':
                return redirect('customer-detail', contact.customer.id)
            else:
                return redirect(fallback)
        else:
            messages.error(request, 'ישנה בעיה בשמירת איש הקשר', extra_tags=contact.full_name)
    context = {
        'form': form,
        'form_header': 'עריכת איש קשר',
    }
    return render(request, 'contacts/contact-form.html', context)

@login_required
def contact_export(request):
    if request.method == "POST":
        contactList = request.POST.get('contactList')
        if contactList:
            contact_ids = [int(id) for id in contactList.split(',')]
            contacts = Contact.objects.filter(id__in=contact_ids)
            return export_to_excel(contacts, filename_prefix="contacts_export")
    return redirect('contact-list')

@login_required
def contact_delete(request, pk):
    if request.method == "POST":
        fallback = request.POST['fallback']
        contact = Contact.objects.get(pk=pk)
        contact.delete()
        messages.success(request, 'איש הקשר נמחק בהצלחה', extra_tags=contact.full_name)
        if fallback == "customer-detail":
            return redirect('customer-detail', contact.customer.id)
        else:
            return redirect('contact-list')
    

@login_required
def contact_set_main(request, pk):
    if request.method == 'POST':
        fallback = request.POST['fallback']
        contact = Contact.objects.get(pk=pk)
        otherContacts = Contact.objects.filter(customer = contact.customer.id).update(is_main = False)
        contact.is_main = True
        contact.save()
        
        if fallback == "customer-detail":
            base_url = reverse(fallback, args=(contact.customer.id,))
            query_string = urlencode({'section': 'contacts'})
            url = f'{base_url}?{query_string}'
            return redirect(url)
        elif fallback == 'contact-detail':
            base_url = reverse(fallback, args=(contact.id,))
            query_string = urlencode({'section': 'notes'})
            url = f'{base_url}?{query_string}'
            return redirect(url)
        else:
            return redirect('contact-list')
    

@login_required
def contact_detail(request, pk):
    contact = Contact.objects.get(pk=pk)
    tagged_note = contact.notes.all().filter(tagged=True).first()

    context = {
        'contact': contact,
        'tagged_note': tagged_note,
    }
    return render(request, 'contacts/contact-detail.html', context)


@login_required
def contact_submit_note(request, pk):
    contact = Contact.objects.get(pk = pk)
    note = Note.objects.create(
        text = request.POST['note'],
        content_object = contact
    )
    base_url = reverse('contact-detail', args=(pk,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

@login_required
def contact_delete_note(request, noteid):
    note = Note.objects.get(pk=noteid)
    contact = Contact.objects.get(pk=note.object_id)
    note.delete()
    messages.success(request, 'הโนוט נמחק בהצלחה', extra_tags=contact.full_name)
    base_url = reverse('contact-detail', args=(contact.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)


@login_required
def contact_tag_note(request, noteid):
    # remove tag from all Notes for this Lead
    note = Note.objects.get(pk=noteid)
    if note.tagged:
        note.tagged = False
    else:
        all_notes = Note.objects.filter(object_id=note.content_object.id).update(tagged=False)
        note.tagged = True
    note.save()
    base_url = reverse('contact-detail', args=(note.content_object.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)


@login_required
def contact_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        contactList = request.POST['contactList']
        contactList = contactList.split(',')
        for l in contactList:
            l = int(l)
            contact = Contact.objects.get(pk=l)
            contact.delete()
        messages.success(request, f'{len(contactList)} אנשי קשר נמחקו בהצלחה')
        return redirect(fallback)


@login_required
def contact_toggle_alerts(request, pk):
    contact = Contact.objects.get(pk = pk)
    contact.is_alerts = not contact.is_alerts
    fallback = request.POST['fallback']
    contact.save()
    if fallback == 'customer-detail':
        base_url = reverse('customer-detail', args=(contact.customer.id,))
        query_string = urlencode({'section': 'contacts'})
        url = f'{base_url}?{query_string}'
        return redirect(url)
    elif fallback == 'contact-detail':
        base_url = reverse('contact-detail', args=(contact.id,))
        query_string = urlencode({'section': 'notes'})
        url = f'{base_url}?{query_string}'
        return redirect(url)
    else:
        return redirect('contact-list')
    
        
    base_url = reverse('contact-detail', args=(pk,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)

