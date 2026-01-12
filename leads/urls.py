from django.urls import path
from . import views

urlpatterns = [
    path('kanban', views.lead_kanban, name='lead-kanban'),
    path('table', views.lead_list, name='lead-list'),
    path('create', views.lead_create, name='lead-create'),
    path('<pk>/edit/<fallback>', views.lead_edit, name='lead-edit'),
    path('<pk>/delete', views.lead_delete, name='lead-delete'),
    path('massdelete/', views.lead_mass_delete, name='lead-mass-delete'),
    path('<pk>/', views.lead_detail, name='lead-detail'),
    path('api/leadsource/create', views.lead_source_create, name='lead-source-create'),
    path('<pk>/note/new', views.lead_submit_note, name='lead-submit-note'),
    path('api/note/<noteid>/delete', views.lead_delete_note, name='lead-delete-note'),
    path('api/note/<noteid>/tagging', views.lead_tag_note, name='lead-tag-note'),
    path('api/update-status', views.lead_update_status, name='lead-update-status'),
    path('api/lead-convert/<pk>', views.lead_convert, name='lead-convert'),
]