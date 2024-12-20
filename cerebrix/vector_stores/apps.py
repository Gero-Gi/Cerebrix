from django.apps import AppConfig


class VectorStoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vector_stores'

    def ready(self):
        import vector_stores.signals
