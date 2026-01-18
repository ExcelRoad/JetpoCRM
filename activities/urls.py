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
]