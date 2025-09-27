from rest_framework import serializers
from .models import Files, APIKeys

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['id', 'user', 'file', 'database', 'time']

# Chats model removed; frontend stores chat session in localStorage and can POST to download endpoint

class APIKeysSerializer(serializers.ModelSerializer):
    has_key = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = APIKeys
        # do NOT expose the api_key field
        fields = ['id', 'user', 'has_key']

    def get_has_key(self, obj):
        return bool(obj.api_key)