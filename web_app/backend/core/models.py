from django.db import models
from django.conf import settings

def user_data_path(instance, filename):
    return f"{instance.user.id}/data/{filename}"

class Files(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    database = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_data_path, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    size = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.database} ({self.user})"

class Chats(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chats = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chats of {self.user}"

class APIKeys(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    api_key = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"API key for {self.user}"

class UserLimits(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    max_chats = models.IntegerField(default=999)
    max_gb_db = models.IntegerField(default=999)

    def __str__(self):
        return f"Limits for {self.user}"

class DailyUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    chats_used = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")