from django.apps import AppConfig


class GamesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.games'
    verbose_name = 'Oyunlar'

    def ready(self):
        import apps.games.signals  # noqa 