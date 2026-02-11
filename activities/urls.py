from django.urls import path
from . import views

urlpatterns = [
    path('api/service/getInfo/<pk>', views.get_service_info, name='get-service-info'),
    path('api/tasks/createupdate/<pk>', views.task_create_update, name='task-create-update'),
    path('api/tasks/complete/<pk>/<main>', views.task_complete, name='task-complete'),
    path('api/tasks/delete/<pk>', views.task_delete, name='task-delete'),
    path('api/timesheets/createudpate/<pk>', views.timesheet_create_update, name= 'timesheet-create-update'),
    path('api/timesheets/delete/<pk>', views.timesheet_delete, name= 'timesheet-delete'),
    path('api/tasks/masscomplete/', views.task_mass_complete, name='task-mass-complete'),
    path('api/task-export/', views.task_export, name='task-export'),
    path('api/tasks/uncomplete/<pk>/', views.task_uncomplete, name='task-uncomplete'),
    path('api/leadsource/save', views.leadsource_save, name='leadsource-save'),
    path('api/leadsource/<pk>/delete', views.leadsource_delete, name='leadsource-delete'),
    path('api/lostreason/save', views.lostreason_save, name='lostreason-save'),
    path('api/lostreason/<pk>/delete', views.lostreason_delete, name='lostreason-delete'),
    path('api/meetings/delete/<pk>', views.meeting_delete, name='meeting-delete'),
    path('api/meetings/createupdate/<pk>', views.meeting_create_update, name='meeting-create-update'),
    path('api/meetings/complete/<pk>', views.meeting_complete, name='meeting-complete'),
    path('api/service/delete/<pk>', views.service_delete, name='service-delete'),
    path('api/service/save', views.service_save, name='service-save'),
]