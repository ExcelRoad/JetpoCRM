from django.urls import path
from . import views

urlpatterns = [
    path('table', views.customer_list, name='customer-list'),
    path('cards/', views.customer_card, name='customer-card'),
    path('create', views.customer_create, name='customer-create'),
    path('<pk>/edit/<fallback>', views.customer_edit, name='customer-edit'),
    path('<pk>/delete', views.customer_delete, name='customer-delete'),
    path('massdelete/', views.customer_mass_delete, name='customer-mass-delete'),
    path('<pk>/', views.customer_detail, name='customer-detail'),
    path('<pk>/note/new', views.customer_submit_note, name='customer-submit-note'),
    path('api/note/<noteid>/delete', views.customer_delete_note, name='customer-delete-note'),
    path('api/note/<noteid>/tagging', views.customer_tag_note, name='customer-tag-note'),
]