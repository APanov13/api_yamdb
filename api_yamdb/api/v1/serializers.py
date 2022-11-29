import datetime as dt
from django.contrib.auth import authenticate
from django.core.validators import MaxValueValidator
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User


class TokenSerializer(serializers.Serializer):
    "Token serializer."

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        fields = ('username', 'confirmation_code')

    def validate(self, attrs):
        user = authenticate(
            username=attrs['username'],
            confirmation_code=attrs['confirmation_code']
        )

        token = RefreshToken.for_user(user)

        return {
            'refresh': str(token),
            'access': str(token.access_token)
        }


class UserSerializerForAdmin(serializers.ModelSerializer):
    """User model serializer for admin."""

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        model = User
        unique = ('username', 'email')

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Используйте другое имя')
        return username


class UserSerializerForUser(UserSerializerForAdmin):
    """User model serializer for user."""

    class Meta(UserSerializerForAdmin.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """Category model serializer."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Genre model serializer."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Title model serializer."""

    genre = serializers.SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug'
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    year = serializers.IntegerField(
        validators=[MaxValueValidator(dt.date.today().year)]
    )
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre',
            'category', 'rating',
        )


class TitleReadSerializer(serializers.ModelSerializer):
    """Read only title model serializer."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre',
            'category', 'rating',
        )
        read_only_fields = ('__all__',)


class ReviewSerializer(serializers.ModelSerializer):
    """Review model serializer."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('title', 'id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title', 'author')

    def validate(self, attrs):
        request = self.context['request']
        if (request.method == 'POST'
                and request.user.reviews.filter(
                title__id=request.parser_context['kwargs']['title_id']
                ).exists()):
            raise serializers.ValidationError(
                'Можно оставить только один отзыв')

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Comment model serializer."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('review', 'id', 'author', 'text', 'pub_date')
        read_only_fields = ('review',)
