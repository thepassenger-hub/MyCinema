from django.apps import AppConfig


class LiveChatConfig(AppConfig):
    name = 'live_chat'

    def ready(self):
        import live_chat.signals