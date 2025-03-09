from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    # Film işlemleri
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('movies/popular/', views.PopularMoviesView.as_view(), name='popular_movies'),
    path('movies/upcoming/', views.UpcomingMoviesView.as_view(), name='upcoming_movies'),
    path('movies/top-rated/', views.TopRatedMoviesView.as_view(), name='top_rated_movies'),
    path('movies/search/', views.MovieSearchView.as_view(), name='movie_search'),
    
    # Film türleri
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    path('genres/<int:pk>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('genres/<int:pk>/movies/', views.GenreMoviesView.as_view(), name='genre_movies'),
    
    # Oyuncular ve ekip
    path('people/', views.PersonListView.as_view(), name='person_list'),
    path('people/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('people/<int:pk>/movies/', views.PersonMoviesView.as_view(), name='person_movies'),
    path('people/search/', views.PersonSearchView.as_view(), name='person_search'),
    
    # Kullanıcı film listeleri
    path('lists/', views.UserMovieListView.as_view(), name='user_lists'),
    path('lists/create/', views.UserMovieListCreateView.as_view(), name='create_list'),
    path('lists/<int:pk>/', views.UserMovieListDetailView.as_view(), name='list_detail'),
    path('lists/<int:pk>/update/', views.UserMovieListUpdateView.as_view(), name='update_list'),
    path('lists/<int:pk>/delete/', views.UserMovieListDeleteView.as_view(), name='delete_list'),
    path('lists/<int:pk>/items/', views.UserMovieListItemView.as_view(), name='list_items'),
    
    # Film değerlendirmeleri
    path('movies/<int:movie_id>/ratings/', views.MovieRatingListView.as_view(), name='movie_ratings'),
    path('movies/<int:movie_id>/rate/', views.RateMovieView.as_view(), name='rate_movie'),
    path('ratings/<int:pk>/', views.MovieRatingDetailView.as_view(), name='rating_detail'),
    path('ratings/<int:pk>/like/', views.MovieRatingLikeView.as_view(), name='like_rating'),
    
    # İzleme listesi
    path('watchlist/', views.WatchlistView.as_view(), name='watchlist'),
    path('watchlist/add/<int:movie_id>/', views.WatchlistAddView.as_view(), name='add_to_watchlist'),
    path('watchlist/remove/<int:movie_id>/', views.WatchlistRemoveView.as_view(), name='remove_from_watchlist'),
    
    # AI önerileri
    path('recommendations/movies/', views.MovieRecommendationsView.as_view(), name='movie_recommendations'),
    path('recommendations/users/', views.UserRecommendationsView.as_view(), name='user_recommendations'),
    path('recommendations/lists/', views.ListRecommendationsView.as_view(), name='list_recommendations'),
] 