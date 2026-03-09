from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class BotApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        key = request.headers.get("X-BOT-KEY")
        if not key or key != settings.BOT_API_KEY:
            raise AuthenticationFailed("Invalid bot key")
        return (None, None)
