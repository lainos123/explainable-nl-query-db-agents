from django.contrib import admin
from .models import Chat, File, Chat

# Register your models here.
admin.site.register(File) # For SQL file upload logging
admin.site.register(Chat) # For user-agent chat logging