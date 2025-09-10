from rest_framework import serializers
from .models import ChatHistory, Files

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['id', 'file', 'time']

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = ['id', 'time', 'user', 'agent', 'prompt', 'response']