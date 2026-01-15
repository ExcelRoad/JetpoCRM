from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment-list'),
    path('api/payments/delete/<pk>', views.payment_delete, name='payment-delete'),
    path('api/payments/<pk>/edit/', views.payment_edit, name='payment-edit'),
    path('api/payments/mass-delete/', views.payment_mass_delete, name='payment-mass-delete'),
]