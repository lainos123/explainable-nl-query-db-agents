"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# TODO: DEMOTRATION ONLY: WILL BE ADDED DURING DEVELOPMENT
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # Include URLs from the core app
]

# Upload will use Django's static file serving in both development and production
# As this is a small-scale project, we can afford this for simplicity
# Futher optimization with a dedicated media server are currently out of scope

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
