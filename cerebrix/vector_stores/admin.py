from django.contrib import admin

# Register your models here.
from django.contrib import admin
from vector_stores.models import VectorStoreBackend, VectorStore, Document, VectorDocument


@admin.register(VectorStoreBackend)
class VectorStoreBackendAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'embedding_model')
    search_fields = ('name', 'description')


@admin.register(VectorStore) 
class VectorStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend', 'code')
    search_fields = ('name', 'description', 'code')
    list_filter = ('backend',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'public', 'hash')
    search_fields = ('name', 'description')
    list_filter = ('public', 'user')


@admin.register(VectorDocument)
class VectorDocumentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'store',)
    list_filter = ('store',)
