
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('users.urls')),
    path('leads/', include('leads.urls')),
    path('quotes/', include('quotes.urls')),
    path('customers/', include('customers.urls')),
    path('contacts/', include('contacts.urls')),
    path('activities/', include('activities.urls')),
    path('projects/', include('projects.urls')),
    path('payments/', include('payments.urls')),
    path("admin/", admin.site.urls)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
