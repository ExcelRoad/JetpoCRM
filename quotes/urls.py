from django.urls import path
from . import views

urlpatterns = [
    path('table', views.quote_list, name='quote-list'),
    path('kanban', views.quote_kanban, name='quote-kanban'),
    path('<pk>/delete', views.quote_delete, name='quote-delete'),
    path('<content_type>/<object_id>/create', views.quote_create, name='quote-create'),
    path('<pk>/edit/<fallback>', views.quote_edit, name='quote-edit'),
    path('<pk>/', views.quote_detail, name='quote-detail'),
    path('<pk>/confirm', views.quote_confirm, name='quote-confirm'),
    path('massdelete/', views.quote_mass_delete, name='quote-mass-delete'),
    path('<pk>/note/new', views.quote_submit_note, name='quote-submit-note'),
    path('api/note/<noteid>/delete', views.quote_delete_note, name='quote-delete-note'),
    path('api/note/<noteid>/tagging', views.quote_tag_note, name='quote-tag-note'),
    path('api/update-status', views.quote_update_status, name='quote-update-status'),
    path('api/get-service-row', views.get_service_form_row, name='get-service-form-row'),
    path('api/get-payment-row', views.get_payment_form_row, name='get-payment-form-row'),
]