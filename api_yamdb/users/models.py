from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model class."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор')
    )

    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True
    )

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True
    )
    role = models.CharField(
        'Роль',
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )

    @property
    def is_admin(self):
        return (self.is_superuser
                or self.is_staff
                or self.role == self.ADMIN)

    @property
    def is_moderator(self):
        return (self.is_admin
                or self.role == self.MODERATOR)
