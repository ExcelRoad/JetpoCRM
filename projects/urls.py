from django.urls import path
from . import views

urlpatterns = [
    path('table', views.project_list, name='project-list'),
    path('<pk>/delete', views.project_delete, name='project-delete'),
    path('<customerId>/create', views.project_create, name='project-create'),
    path('create', views.project_create, name='project-create'),
    path('api/project-export/', views.project_export, name='project-export'),
    path('import-template/', views.project_import_template, name='project-import-template'),
    path('api/import-preview/', views.project_import_preview, name='project-import-preview'),
    path('import-confirm/', views.project_import_confirm, name='project-import-confirm'),
    path('massdelete/', views.project_mass_delete, name='project-mass-delete'),
    path('<pk>/edit/<fallback>', views.project_edit, name='project-edit'),
    path('<pk>/', views.project_detail, name='project-detail'),
    path('<pk>/note/new', views.project_submit_note, name='project-submit-note'),
    path('api/note/<noteid>/delete', views.project_delete_note, name='project-delete-note'),
    path('api/note/<noteid>/tagging', views.project_tag_note, name='project-tag-note'),
    path('api/budgets/makeactive/<pk>', views.project_budget_activate, name='project-budget-activate'),
    path('api/budgets/delete/<pk>', views.budget_delete,name='budget-delete'),
    path('apk/budgets/createupdate/<pk>', views.budget_create_update, name='budget-create-update'),
    path('api/budgets/addbudget/<pk>', views.budget_add, name='budget-add'),
]