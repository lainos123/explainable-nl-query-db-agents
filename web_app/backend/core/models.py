from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

# Create your models here.

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'
class Files(models.Model):
    # SQL DB logging to store uploaded SQL files
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # File send to /backend/media/sql_files/
    file = models.FileField(upload_to=user_directory_path)
    time = models.DateTimeField(auto_now_add=True)

# Delete file from storage when deleted from DB
@receiver(post_delete, sender=Files)
def delete_file_and_empty_folder(sender, instance, **kwargs):
    if instance.file and instance.file.path:
        file_path = instance.file.path
        folder_path = os.path.dirname(file_path)

        # Remove file
        if os.path.isfile(file_path):
            os.remove(file_path)

        # If folder is empty, remove folder
        if os.path.isdir(folder_path) and not os.listdir(folder_path):
            os.rmdir(folder_path)

class Sessions(models.Model):
    # Store user sessions for chat history
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)

class Chats(models.Model):
    # Log of user queries and corresponding SQL queries
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, related_name='chats')
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.CharField(max_length=1) # Name as a, b, c, d
    # Type of the response: sql, text, json, etc.
    type = models.CharField(max_length=10)
    prompt = models.TextField()
    response = models.TextField()

class APIKeys(models.Model):
    # Store API keys for different LLMs
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api_key = models.TextField()
