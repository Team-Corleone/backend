import django_filters
from .models import Movie

class MovieFilter(django_filters.FilterSet):
    """Film filtreleme"""
    title = django_filters.CharFilter(lookup_expr='icontains')
    original_title = django_filters.CharFilter(lookup_expr='icontains')
    release_date_after = django_filters.DateFilter(field_name='release_date', lookup_expr='gte')
    release_date_before = django_filters.DateFilter(field_name='release_date', lookup_expr='lte')
    runtime_min = django_filters.NumberFilter(field_name='runtime', lookup_expr='gte')
    runtime_max = django_filters.NumberFilter(field_name='runtime', lookup_expr='lte')
    genres = django_filters.CharFilter(field_name='genres__name', lookup_expr='icontains')
    cast = django_filters.CharFilter(field_name='cast__name', lookup_expr='icontains')
    crew = django_filters.CharFilter(field_name='crew__name', lookup_expr='icontains')

    class Meta:
        model = Movie
        fields = [
            'title', 'original_title', 'release_date_after',
            'release_date_before', 'runtime_min', 'runtime_max',
            'genres', 'cast', 'crew'
        ] 