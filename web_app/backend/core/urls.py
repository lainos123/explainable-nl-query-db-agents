from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, ChatViewSet

# Register viewsets with the router
router = DefaultRouter()

# TODO: Add more viewsets as needed
router.register(r'file', FileViewSet)
router.register(r'chat', ChatViewSet)

# Define the URL patterns for the core app
urlpatterns = [
    path('', include(router.urls)),
]