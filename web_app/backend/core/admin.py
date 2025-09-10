from django.contrib import admin
from .models import Files, ChatHistory

# Register your models here.
admin.site.register(Files) # For SQL file upload logging
admin.site.register(ChatHistory) # For user-agent chat history logging