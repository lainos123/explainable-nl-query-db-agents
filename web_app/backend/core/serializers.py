from rest_framework import serializers
from .models import Files, Chats, APIKeys

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['id', 'user', 'file', 'database', 'time']

class ChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chats
        fields = ['id', 'user', 'chats', 'time']

class APIKeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKeys
        fields = ['id', 'user', 'api_key']