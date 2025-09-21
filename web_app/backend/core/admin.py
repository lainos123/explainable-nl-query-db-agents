from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Files, Sessions, Chats, APIKey

# Register your models here.
admin.site.register(Files) # For file upload logging
admin.site.register(Sessions) # For session logging
admin.site.register(Chats) # For chat logging
@admin.register(APIKey)
class APIKeyAdmin(SingletonModelAdmin):
    pass