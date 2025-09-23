import os
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Files, APIKeys

# Delete file from filesystem when Files instance is deleted
@receiver(post_delete, sender=Files)
def delete_file_and_empty_folder(sender, instance, **kwargs):
    if instance.file and instance.file.path:
        file_path = instance.file.path
        # Use MEDIA_ROOT from Django settings for folder path
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root:
            # Get relative path to MEDIA_ROOT
            rel_path = os.path.relpath(file_path, media_root)
            folder_path = os.path.join(media_root, os.path.dirname(rel_path))
        else:
            folder_path = os.path.dirname(file_path)

        if os.path.isfile(file_path):
            os.remove(file_path)

        if os.path.isdir(folder_path) and not os.listdir(folder_path):
            os.rmdir(folder_path)

# Update cache when APIKey instance is saved
@receiver(post_save, sender=APIKeys)
def update_api_key_cache(sender, instance, **kwargs):
    cache.set("api_key_value", instance.api_key, None)
