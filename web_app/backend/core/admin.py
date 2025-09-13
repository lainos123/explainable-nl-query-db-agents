from django.contrib import admin
from .models import Files, Sessions, Chats, APIKeys

# Register your models here.
admin.site.register(Files) # For file upload logging
admin.site.register(Sessions) # For session logging
admin.site.register(Chats) # For chat logging
admin.site.register(APIKeys) # For API key management
