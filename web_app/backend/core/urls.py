from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FilesViewSet, ChatsViewSet, APIKeysViewSet

# Register viewsets with the router
router = DefaultRouter()

# TODO: Add more viewsets as needed
router.register(r'files', FilesViewSet, basename='files')
router.register(r'chats', ChatsViewSet, basename='chats')
router.register(r'apikeys', APIKeysViewSet, basename='apikeys')

urlpatterns = router.urls
