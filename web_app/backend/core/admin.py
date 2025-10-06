from django.contrib import admin
from .models import Files, Chats, APIKeys, UserLimits, DailyUsage


@admin.register(Files)
class FilesAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "database", "size", "time")
	list_filter = ("user",)
	search_fields = ("database",)

@admin.register(Chats)
class ChatsAdmin(admin.ModelAdmin):
	list_display = ("user", "time")
	search_fields = ("user__username",)

@admin.register(APIKeys)
class APIKeysAdmin(admin.ModelAdmin):
	list_display = ("user",)


@admin.register(UserLimits)
class UserLimitsAdmin(admin.ModelAdmin):
	list_display = ("user", "max_chats", "max_gb_db")
	search_fields = ("user__username",)

@admin.register(DailyUsage)
class DailyUsageAdmin(admin.ModelAdmin):
	list_display = ("user", "date", "chats_used")
	list_filter = ("date",)
	search_fields = ("user__username",)
