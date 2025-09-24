from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FilesViewSet, APIKeysViewSet, UsageView, download_chat_markdown, chats_view

# Register viewsets with the router
router = DefaultRouter()
router.register(r'files', FilesViewSet, basename='files')
router.register(r'apikeys', APIKeysViewSet, basename='apikeys')

urlpatterns = [
	path('usage/', UsageView.as_view(), name='usage'),
	path('download-chat-md/', download_chat_markdown, name='download-chat-md'),
	path('chats/', chats_view, name='chats'),
]

# include router URLs after custom ones
urlpatterns += router.urls
