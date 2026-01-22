from django.urls import path
from . import views

urlpatterns = [
    path('change_lead_alert_settings', views.change_lead_alert_settings, name='change_lead_alert_settings'),
]