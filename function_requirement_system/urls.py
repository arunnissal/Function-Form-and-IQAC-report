from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('accounts.urls')),
    path('requests/', include('requests.urls')),
    path('approvals/', include('approvals.urls')),
    path('reports/', include('reports.urls')),
    path('halls/', include('halls.urls')),
    path('departments/', include('departments.urls')),
    path('documents/', include('event_documents.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
