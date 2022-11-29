from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter
from titles.models import Title


class TitleFilter(FilterSet):
    """"Django backend filter for title model."""

    genre = CharFilter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )
    category = CharFilter(
        field_name='category__slug',
        lookup_expr='icontains'
    )
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    year = NumberFilter(
        field_name='year',
    )

    class Meta:
        model = Title
        fields = '__all__'
