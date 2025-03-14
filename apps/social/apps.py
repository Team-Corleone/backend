from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.social'
    verbose_name = 'Sosyal'

    def ready(self):
        import apps.social.signals  # noqa 