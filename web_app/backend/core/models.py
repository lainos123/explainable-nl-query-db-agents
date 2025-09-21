from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from solo.models import SingletonModel

# Create your models here.
def data_path(instance, filename):
    # file will be uploaded to data/<filename>
    return f'data/{filename}'

class Files(models.Model):
    file = models.FileField(upload_to=data_path)
    database = models.CharField(max_length=255, blank=True)
    time = models.DateTimeField(auto_now_add=True)

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

class APIKey(SingletonModel):
    # API One-Record table
    api_key = models.TextField()
    def __str__(self):
        return "API Key"
