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

# TODO: DEMOTRATION ONLY: WILL BE ADDED DURING DEVELOPMENT
urlpatterns = [
    path("admin/", admin.site.urls),

    # API docs and entrypoints
    # GET /api/docs -> Swagger UI
    # GET /api/apis -> json of available APIs, endpoints, and parameters
    path("api/", include("api.urls")),  

    # Database management
    # POST /data/add -> add one file only
    # POST /data/add-zip -> add multiple files in a zip
    # DELETE /data/{id} -> remove
    # GET /data/list -> list
    # GET /data/{id}/schema -> schema
    # GET /data/download/{id} -> download original file
    # GET /data/download-zip -> download all files in a zip
    # GET /data/query?{sql-query} -> SQL query
    path("data/", include("db.urls")),

    # Agent query
    # GET /agent/a
    # GET /agent/a?{actions} # last, change-last, add-last, remove-last, delete-all, receive-all
    # GET /agent/b
    # GET /agent/c
    # GET /agent/d
    path("agent/", include("query.urls")),
]
