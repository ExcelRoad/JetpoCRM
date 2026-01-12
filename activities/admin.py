from django.contrib import admin
from .models import Note, Task, Service, Timesheet

admin.site.register(Note)
admin.site.register(Task)
admin.site.register(Service)
admin.site.register(Timesheet)