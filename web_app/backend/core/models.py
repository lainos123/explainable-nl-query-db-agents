from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from solo.models import SingletonModel

# Create your models here.
def data_path(instance, filename):
    # file will be uploaded to data/<filename>
    return f'data/{filename}'

class Files(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Store uploaded files
    file = models.FileField(upload_to=data_path)
    database = models.CharField(max_length=255, blank=True)
    time = models.DateTimeField(auto_now_add=True)

class Chats(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chats = models.TextField()  # Store chat history as text
    time = models.DateTimeField(auto_now_add=True) # Last updated time

    # user is PK
    class Meta:
        unique_together = ('user',)

class APIKeys(SingletonModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api_key = models.TextField(blank=True, null=True)

    # user is PK
    class Meta:
        unique_together = ('user',)
