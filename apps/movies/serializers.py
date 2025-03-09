from rest_framework import serializers
from .models import (
    Movie, Genre, Person, MovieCast, MovieCrew,
    UserMovieList, UserMovieListItem, UserMovieRating, UserMovieWatchlist
)

class GenreSerializer(serializers.ModelSerializer):
    """Film türü serializerı"""
    class Meta:
        model = Genre
        fields = ('id', 'name', 'description')

class PersonSerializer(serializers.ModelSerializer):
    """Kişi serializerı"""
    class Meta:
        model = Person
        fields = (
            'id', 'name', 'bio', 'photo', 'birth_date',
            'death_date', 'imdb_id', 'tmdb_id'
        )

class MovieCastSerializer(serializers.ModelSerializer):
    """Film oyuncu kadrosu serializerı"""
    person = PersonSerializer(read_only=True)

    class Meta:
        model = MovieCast
        fields = ('id', 'person', 'character', 'order')

class MovieCrewSerializer(serializers.ModelSerializer):
    """Film ekibi serializerı"""
    person = PersonSerializer(read_only=True)

    class Meta:
        model = MovieCrew
        fields = ('id', 'person', 'department', 'job')

class MovieSerializer(serializers.ModelSerializer):
    """Film serializerı"""
    genres = GenreSerializer(many=True, read_only=True)
    cast = MovieCastSerializer(source='moviecast_set', many=True, read_only=True)
    crew = MovieCrewSerializer(source='moviecrew_set', many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    is_in_watchlist = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = (
            'id', 'title', 'original_title', 'overview',
            'poster', 'backdrop', 'release_date', 'runtime',
            'budget', 'revenue', 'imdb_id', 'tmdb_id',
            'genres', 'cast', 'crew', 'average_rating',
            'ratings_count', 'user_rating', 'is_in_watchlist'
        )

    def get_average_rating(self, obj):
        ratings = obj.user_ratings.all()
        if not ratings:
            return None
        return sum(r.rating for r in ratings) / len(ratings)

    def get_ratings_count(self, obj):
        return obj.user_ratings.count()

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = obj.user_ratings.get(user=request.user)
                return rating.rating
            except UserMovieRating.DoesNotExist:
                pass
        return None

    def get_is_in_watchlist(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserMovieWatchlist.objects.filter(
                user=request.user,
                movie=obj
            ).exists()
        return False

class UserMovieListSerializer(serializers.ModelSerializer):
    """Kullanıcı film listesi serializerı"""
    user = serializers.StringRelatedField(read_only=True)
    movies_count = serializers.SerializerMethodField()

    class Meta:
        model = UserMovieList
        fields = (
            'id', 'user', 'name', 'description', 'is_public',
            'created_at', 'updated_at', 'movies_count'
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_movies_count(self, obj):
        return obj.movies.count()

class UserMovieListItemSerializer(serializers.ModelSerializer):
    """Film listesi öğesi serializerı"""
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserMovieListItem
        fields = ('id', 'movie', 'movie_id', 'notes', 'added_at', 'order')
        read_only_fields = ('added_at',)

class UserMovieRatingSerializer(serializers.ModelSerializer):
    """Film değerlendirmesi serializerı"""
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = UserMovieRating
        fields = (
            'id', 'user', 'movie', 'rating', 'review',
            'created_at', 'updated_at', 'likes_count', 'is_liked'
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class UserMovieWatchlistSerializer(serializers.ModelSerializer):
    """İzleme listesi serializerı"""
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = UserMovieWatchlist
        fields = ('id', 'movie', 'added_at', 'notes')
        read_only_fields = ('added_at',) 