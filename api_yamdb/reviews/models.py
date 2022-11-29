from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from titles.models import Title

User = get_user_model()


class TextPubDateModel(models.Model):
    """Abstract model for text and pub date."""

    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        text_str_length: int = 15
        return self.text[:text_str_length]


class Review(TextPubDateModel):
    """Review model class."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(MinValueValidator(1), MaxValueValidator(10))
    )

    class Meta:
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                name='unique_title_author',
                fields=('title', 'author'),
            ),
        ]


class Comment(TextPubDateModel):
    """Comment model class."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, verbose_name='Отзыв')

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
