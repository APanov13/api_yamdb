from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupView,
    TitleViewSet,
    TokenView,
    UserViewSet,
)

auth_patterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token_obtain')
]

router = DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'),
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'),
router.register('users', UserViewSet, basename='user')
router.register('genres', GenreViewSet, basename='genre')
router.register('titles', TitleViewSet, basename='title')
router.register('categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_patterns)),
]
