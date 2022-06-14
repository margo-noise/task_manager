"""task_manager URL Configuration"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('labels/', include('task_manager.apps.label.urls')),
]
