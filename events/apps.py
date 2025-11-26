from django.apps import AppConfig

class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"

    def ready(self):
        # import signals so they are registered
        from . import signals  # noqa: F401