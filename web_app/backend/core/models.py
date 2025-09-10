from django.db import models

# Create your models here.
class Files(models.Model):
    # SQL DB logging to store uploaded SQL files
    id = models.AutoField(primary_key=True)
    # File send to /backend/media/sql_files/
    file = models.FileField(upload_to='sql_files/')
    time = models.DateTimeField(auto_now_add=True)

class ChatHistory(models.Model):
    # Log of user queries and corresponding SQL queries
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    agent = models.CharField(max_length=1) # Name as a, b, c, d
    prompt = models.TextField()
    response = models.TextField()

