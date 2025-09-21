from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FilesViewSet, SessionsViewSet, ChatsViewSet, APIKeyViewSet

# Register viewsets with the router
router = DefaultRouter()

# TODO: Add more viewsets as needed
router.register(r'files', FilesViewSet, basename='files')
router.register(r'sessions', SessionsViewSet, basename='sessions')
router.register(r'chats', ChatsViewSet, basename='chats')
router.register(r'apikey', APIKeyViewSet, basename='apikey')

urlpatterns = router.urls
