from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment-list'),
    path('api/payments/delete/<pk>', views.payment_delete, name='payment-delete'),
    path('api/payment-export/', views.payment_export, name='payment-export'),
    path('api/payments/<pk>/edit/', views.payment_edit, name='payment-edit'),
    path('api/payments/mass-delete/', views.payment_mass_delete, name='payment-mass-delete'),
    path('api/payments/send-invoice/<pk>', views.payment_send_invoice, name = 'payment-send-invoice'),
    path('api/payments/send-receipt/<pk>', views.payment_send_recipt, name = 'payment-send-receipt'),
]