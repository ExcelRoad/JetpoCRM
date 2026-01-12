from django.urls import path
from . import views

urlpatterns = [
    path('table', views.contact_list, name='contact-list'),
    path('create', views.contact_create, name='contact-create'),
    path('create/<pk>', views.contact_create, name='contact-create'),
    path('<pk>/edit/<fallback>', views.contact_edit, name='contact-edit'),
    path('<pk>/delete', views.contact_delete, name='contact-delete'),
    path('massdelete/', views.contact_mass_delete, name='contact-mass-delete'),
    path('<pk>/', views.contact_detail, name='contact-detail'),
    path('<pk>/note/new', views.contact_submit_note, name='contact-submit-note'),
    path('api/note/<noteid>/delete', views.contact_delete_note, name='contact-delete-note'),
    path('api/note/<noteid>/tagging', views.contact_tag_note, name='contact-tag-note'),
    path('api/set_main/<pk>', views.contact_set_main, name='contact-set-main'),
]