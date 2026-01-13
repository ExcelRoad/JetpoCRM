from django.urls import path
from . import views

urlpatterns = [
    path('api/payments/delete/<pk>', views.payment_delete, name='payment-delete'),
    path('api/payments/<pk>/edit/', views.payment_edit, name='payment-edit'),
]