import django_filters
from .models import Community, CommunityPost, CommunityComment

class CommunityFilter(django_filters.FilterSet):
    """Topluluk filtreleme"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    creator = django_filters.NumberFilter(field_name='creator__id')
    is_private = django_filters.BooleanFilter()
    created_at = django_filters.DateTimeFilter()
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Community
        fields = [
            'name', 'description', 'creator',
            'is_private', 'created_at',
            'created_at_after', 'created_at_before'
        ]

class CommunityPostFilter(django_filters.FilterSet):
    """Topluluk gönderisi filtreleme"""
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.NumberFilter(field_name='author__id')
    community = django_filters.NumberFilter(field_name='community__id')
    is_pinned = django_filters.BooleanFilter()
    is_locked = django_filters.BooleanFilter()
    created_at = django_filters.DateTimeFilter()
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = CommunityPost
        fields = [
            'title', 'content', 'author', 'community',
            'is_pinned', 'is_locked', 'created_at',
            'created_at_after', 'created_at_before'
        ]

class CommunityCommentFilter(django_filters.FilterSet):
    """Topluluk yorumu filtreleme"""
    content = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.NumberFilter(field_name='author__id')
    post = django_filters.NumberFilter(field_name='post__id')
    parent = django_filters.NumberFilter(field_name='parent__id')
    created_at = django_filters.DateTimeFilter()
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = CommunityComment
        fields = [
            'content', 'author', 'post', 'parent',
            'created_at', 'created_at_after', 'created_at_before'
        ] 