from django.contrib import admin
from django.forms.models import model_to_dict


# Register your models here.
from .models import Thread, ThreadMessage, ThreadBackend

class ThreadMessageInline(admin.TabularInline):
    model = ThreadMessage
    extra = 0
    readonly_fields = ('role', 'content_type', 'content_value', 'total_tokens', 'created_at')
    fields = ('role', 'content_type', 'total_tokens', 'content_tokens', 'created_at')
    
   
    
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
    list_filter = ('user', 'backend')
    inlines = [ThreadMessageInline]
    
    def save_model(self, request, obj, form, change):
        if not change:
            dict_obj = model_to_dict(obj)
            Thread.objects.create(**model_to_dict(obj))
        else:
            super().save_model(request, obj, form, change)

admin.site.register(Thread, ThreadAdmin)

class ThreadInline(admin.TabularInline):
    model = Thread
    extra = 0
    can_delete = False
    readonly_fields = ('id', 'name', 'user', 'created_at')
    fields = readonly_fields
    show_change_link = True  # Adds a link to edit the Thread in its own page
    
    def has_add_permission(self, request, obj=None):
        return False

class ThreadBackendAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'chat_model__name',
        'get_thread_count',
        )
    list_filter = ('chat_model__name',)
    search_fields = ('name',)
    inlines = [ThreadInline]
    
    def get_thread_count(self, obj):
        return obj.threads.count()
    get_thread_count.short_description = 'Thread Count'

admin.site.register(ThreadBackend, ThreadBackendAdmin)