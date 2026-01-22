from django.contrib import admin
from .models import AlertType, AlertSettings


admin.site.register(AlertType)
admin.site.register(AlertSettings)
