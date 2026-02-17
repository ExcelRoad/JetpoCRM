from django.urls import path
from . import views

urlpatterns = [
    path('kanban', views.lead_kanban, name='lead-kanban'),
    path('table', views.lead_list, name='lead-list'),
    path('create', views.lead_create, name='lead-create'),
    path('api/lead-export/', views.lead_export, name='lead-export'),
    path('import-template/', views.lead_import_template, name='lead-import-template'),
    path('api/import-preview/', views.lead_import_preview, name='lead-import-preview'),
    path('import-confirm/', views.lead_import_confirm, name='lead-import-confirm'),
    path('api/leadsource/create', views.lead_source_create, name='lead-source-create'),
    path('api/lostreason/create', views.lost_reason_create, name='lost-reason-create'),
    path('api/update-status', views.lead_update_status, name='lead-update-status'),
    path('api/webhook/elementor', views.elementor_webhook, name='elementor-webhook'),
    path('massdelete/', views.lead_mass_delete, name='lead-mass-delete'),
    path('api/leads/mass-delete', views.lead_mass_delete, name='lead-mass-delete'),
    path('<pk>/', views.lead_detail, name='lead-detail'),
    path('<pk>/edit/<fallback>', views.lead_edit, name='lead-edit'),
    path('<pk>/delete', views.lead_delete, name='lead-delete'),
    path('<pk>/note/new', views.lead_submit_note, name='lead-submit-note'),
    path('api/note/<noteid>/delete', views.lead_delete_note, name='lead-delete-note'),
    path('api/note/<noteid>/tagging', views.lead_tag_note, name='lead-tag-note'),
    path('api/lead-convert/<pk>', views.lead_convert, name='lead-convert'),
]