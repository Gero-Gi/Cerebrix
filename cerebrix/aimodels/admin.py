from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget

from .models import LanguageModel

@admin.register(LanguageModel)
class LanguageModelAdmin(admin.ModelAdmin):
    list_display = ["name", "type"] 
    list_filter = ["type"]
    search_fields = ["name"]
    formfield_overrides = {
            JSONField: {'widget': JSONEditorWidget},
        }

 