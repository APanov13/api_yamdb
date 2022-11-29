from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.tokens import default_token_generator
from rest_framework import exceptions
from users.models import User


class AuthBackend(ModelBackend):
    """Provides token authentication."""

    def authenticate(self, request, username=None, confirmation_code=None):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.NotFound('Пользователь не найден')
        if not default_token_generator.check_token(user, confirmation_code):
            raise exceptions.ParseError('Введен неправильный код потверждения')
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
