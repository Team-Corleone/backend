from django.contrib import admin
from .models import (
    Genre, Person, Movie, MovieCast, MovieCrew,
    UserMovieList, UserMovieListItem, UserMovieRating, UserMovieWatchlist
)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'imdb_id', 'tmdb_id')
    search_fields = ('name', 'imdb_id')
    list_filter = ('birth_date',)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'original_title', 'release_date', 'runtime', 'imdb_id')
    search_fields = ('title', 'original_title', 'imdb_id')
    list_filter = ('release_date', 'genres')
    filter_horizontal = ('genres', 'cast', 'crew')

@admin.register(MovieCast)
class MovieCastAdmin(admin.ModelAdmin):
    list_display = ('movie', 'person', 'character', 'order')
    search_fields = ('movie__title', 'person__name', 'character')
    list_filter = ('movie',)

@admin.register(MovieCrew)
class MovieCrewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'person', 'department', 'job')
    search_fields = ('movie__title', 'person__name', 'job')
    list_filter = ('department',)

@admin.register(UserMovieList)
class UserMovieListAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_public', 'created_at')
    search_fields = ('user__username', 'name')
    list_filter = ('is_public',)

@admin.register(UserMovieListItem)
class UserMovieListItemAdmin(admin.ModelAdmin):
    list_display = ('movie_list', 'movie', 'added_at', 'order')
    search_fields = ('movie_list__name', 'movie__title')
    list_filter = ('movie_list',)

@admin.register(UserMovieRating)
class UserMovieRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'created_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('rating',)

@admin.register(UserMovieWatchlist)
class UserMovieWatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    search_fields = ('user__username', 'movie__title') 