from django.contrib import admin

from .models import ChatModel

@admin.register(ChatModel)
class ChatModelAdmin(admin.ModelAdmin):
    list_display = ["name", "type"] 
    list_filter = ["type"]
    search_fields = ["name"]

