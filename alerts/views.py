from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from alerts.models import AlertSettings, AlertType

def change_lead_alert_settings(request):
    if request.method == "POST":
        lead_alert_settings = AlertSettings.objects.get(
            user = request.user,
            alert_type = AlertType.objects.get(slug='leads')
        )

        if request.POST.get('lead_created_email'):
            lead_alert_settings.created_email = True
        else:
            lead_alert_settings.created_email = False

        if request.POST.get('lead_created_in_app'):
            lead_alert_settings.created_in_app = True
        else:
            lead_alert_settings.created_in_app = False

        if request.POST.get('lead_updated_email'):
            lead_alert_settings.updated_email = True
        else:
            lead_alert_settings.updated_email = False

        if request.POST.get('lead_updated_in_app'):
            lead_alert_settings.updated_in_app = True
        else:
            lead_alert_settings.updated_in_app = False

        if request.POST.get('lead_deleted_email'):
            lead_alert_settings.deleted_email = True
        else:
            lead_alert_settings.deleted_email = False

        if request.POST.get('lead_deleted_in_app'):
            lead_alert_settings.deleted_in_app = True
        else:
            lead_alert_settings.deleted_in_app = False

        lead_alert_settings.save()

        base_url = reverse('settings')
        query_string = urlencode({'section': 'leads', 'subsection': '2'})
        url = f'{base_url}?{query_string}'

        return redirect(url)

        

