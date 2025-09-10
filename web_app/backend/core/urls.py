from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FilesViewSet, FilesViewSet, ChatHistoryViewSet

# Register viewsets with the router
router = DefaultRouter()

# TODO: Add more viewsets as needed
router.register(r'files', FilesViewSet)
router.register(r'chat', ChatHistoryViewSet)

# Define the URL patterns for the core app
urlpatterns = [
    path('', include(router.urls)),
]