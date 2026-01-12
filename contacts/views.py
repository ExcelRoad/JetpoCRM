from django.shortcuts import render, redirect
from .models import Contact
from .forms import ContactForm
from django.urls import reverse
from urllib.parse import urlencode
from activities.models import Note

def contact_list(request):
    contacts = Contact.objects.all()
    context = {
        'contacts': contacts,
    }
    return render(request, 'contacts/contact-list.html', context)


def contact_create(request, pk=None):
    if pk == None:
        form = ContactForm()
    else:
        form = ContactForm(initial={'customer': pk})
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            return redirect('contact-detail', contact.id)
    context = {
        'form': form,
        'form_header': 'יצירת איש קשר',
    }
    return render(request, 'contacts/contact-form.html', context)


def contact_edit(request, pk, fallback):
    contact = Contact.objects.get(pk=pk)
    form = ContactForm(instance=contact)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            if fallback == "contact-detail":
                return redirect('contact-detail', contact.id)
            elif fallback == 'customer-detail':
                return redirect('customer-detail', contact.customer.id)
            else:
                return redirect(fallback)
    context = {
        'form': form,
        'form_header': 'עריכת איש קשר',
    }
    return render(request, 'contacts/contact-form.html', context)

def contact_delete(request, pk):
    if request.method == "POST":
        fallback = request.POST['fallback']
        contact = Contact.objects.get(pk=pk)
        contact.delete()
        if fallback == "customer-detail":
            return redirect('customer-detail', contact.customer.id)
        else:
            return redirect('contact-list')
    

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
    

def contact_detail(request, pk):
    contact = Contact.objects.get(pk=pk)
    tagged_note = contact.notes.all().filter(tagged=True).first()

    context = {
        'contact': contact,
        'tagged_note': tagged_note,
    }
    return render(request, 'contacts/contact-detail.html', context)


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

def contact_delete_note(request, noteid):
    note = Note.objects.get(pk=noteid)
    contact = Contact.objects.get(pk=note.object_id)
    note.delete()
    base_url = reverse('contact-detail', args=(contact.id,))
    query_string = urlencode({'section': 'notes'})
    url = f'{base_url}?{query_string}'
    return redirect(url)


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


def contact_mass_delete(request):
    if request.method == "POST":
        fallback = request.POST['fallback']
        contactList = request.POST['contactList']
        contactList = contactList.split(',')
        for l in contactList:
            l = int(l)
            contact = Contact.objects.get(pk=l)
            contact.delete()
        return redirect(fallback)

