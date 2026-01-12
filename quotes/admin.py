from django.contrib import admin
from .models import Quote, Quote_Payment, Quote_Service


admin.site.register(Quote)
admin.site.register(Quote_Payment)
admin.site.register(Quote_Service)
