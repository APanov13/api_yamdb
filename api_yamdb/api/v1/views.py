from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, APIView
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from reviews.models import Review
from titles.models import Category, Genre, Title
from users.models import User
from .utils import ConfirmationManager
from .filters import TitleFilter
from .permissions import AuthorOrStaffOrReadOnly, IsAdmin, IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializerForAdmin,
    UserSerializerForUser
)


class SignupView(APIView):
    """Signup view."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializerForUser(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        ConfirmationManager(user=user).send_code()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(TokenViewBase):
    """Token view."""

    serializer_class = TokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    """User model view set."""

    queryset = User.objects.all()
    lookup_field = 'username'
    permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        if self.request.user.is_admin:
            return UserSerializerForAdmin
        return UserSerializerForUser

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=(permissions.IsAuthenticated,),
            name='My information'
            )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class GenreViewSet(ListCreateDestroyViewSet):
    """Genre model view set."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(ListCreateDestroyViewSet):
    """Category model view set."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Title model view set."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitleSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Review model view set."""

    serializer_class = ReviewSerializer
    permission_classes = (AuthorOrStaffOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Comment model view set."""

    serializer_class = CommentSerializer
    permission_classes = (AuthorOrStaffOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            title__id=self.kwargs.get('title_id'),
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
