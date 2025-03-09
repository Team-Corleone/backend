from rest_framework import generics, filters, status, views
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from .models import (
    Movie, Genre, Person, UserMovieList, UserMovieListItem,
    UserMovieRating, UserMovieWatchlist
)
from .serializers import (
    MovieSerializer, GenreSerializer, PersonSerializer,
    UserMovieListSerializer, UserMovieListItemSerializer,
    UserMovieRatingSerializer, UserMovieWatchlistSerializer
)
from .filters import MovieFilter
from .permissions import IsOwnerOrReadOnly

class MovieListView(generics.ListAPIView):
    """Film listesi"""
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MovieFilter
    search_fields = ['title', 'original_title']
    ordering_fields = ['release_date', 'runtime']

class MovieDetailView(generics.RetrieveAPIView):
    """Film detayı"""
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

class PopularMoviesView(generics.ListAPIView):
    """Popüler filmler"""
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Movie.objects.all().order_by('-user_ratings__rating')[:20]

class UpcomingMoviesView(generics.ListAPIView):
    """Yaklaşan filmler"""
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Movie.objects.filter(release_date__gt=timezone.now()).order_by('release_date')[:20]

class TopRatedMoviesView(generics.ListAPIView):
    """En çok beğenilen filmler"""
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Movie.objects.all().order_by('-user_ratings__rating')[:20]

class MovieSearchView(generics.ListAPIView):
    """Film arama"""
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'original_title', 'overview']

class GenreListView(generics.ListAPIView):
    """Film türleri listesi"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

class GenreDetailView(generics.RetrieveAPIView):
    """Film türü detayı"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

class GenreMoviesView(generics.ListAPIView):
    """Belirli bir türe ait filmler"""
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Movie.objects.filter(genres__id=self.kwargs['pk'])

class PersonListView(generics.ListAPIView):
    """Kişiler listesi"""
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class PersonDetailView(generics.RetrieveAPIView):
    """Kişi detayı"""
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

class PersonSearchView(generics.ListAPIView):
    """Kişi arama"""
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class PersonMoviesView(generics.ListAPIView):
    """Kişinin filmleri"""
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Movie.objects.filter(
            models.Q(cast__id=self.kwargs['pk']) |
            models.Q(crew__id=self.kwargs['pk'])
        ).distinct()

class UserMovieListView(generics.ListAPIView):
    """Kullanıcı film listeleri"""
    serializer_class = UserMovieListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserMovieList.objects.filter(user=self.request.user)

class UserMovieListCreateView(generics.CreateAPIView):
    """Film listesi oluşturma"""
    serializer_class = UserMovieListSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserMovieListDetailView(generics.RetrieveAPIView):
    """Film listesi detayı"""
    serializer_class = UserMovieListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.method == 'GET':
            return UserMovieList.objects.filter(is_public=True)
        return UserMovieList.objects.filter(user=self.request.user)

class UserMovieListUpdateView(generics.UpdateAPIView):
    """Film listesi güncelleme"""
    serializer_class = UserMovieListSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return UserMovieList.objects.filter(user=self.request.user)

class UserMovieListDeleteView(generics.DestroyAPIView):
    """Film listesi silme"""
    serializer_class = UserMovieListSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return UserMovieList.objects.filter(user=self.request.user)

class UserMovieListItemView(generics.ListCreateAPIView):
    """Film listesi öğeleri"""
    serializer_class = UserMovieListItemSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return UserMovieListItem.objects.filter(movie_list_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        movie_list = get_object_or_404(UserMovieList, id=self.kwargs['pk'])
        if movie_list.user != self.request.user:
            return Response(
                {'detail': 'Bu listeye film ekleyemezsiniz.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(movie_list=movie_list)

class MovieRatingListView(generics.ListCreateAPIView):
    """Film değerlendirmeleri"""
    serializer_class = UserMovieRatingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserMovieRating.objects.filter(movie_id=self.kwargs['movie_id'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, movie_id=self.kwargs['movie_id'])

class RateMovieView(generics.CreateAPIView):
    """Film değerlendirme"""
    serializer_class = UserMovieRatingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            movie_id=self.kwargs['movie_id']
        )

class MovieRatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Film değerlendirmesi detay, güncelleme ve silme"""
    serializer_class = UserMovieRatingSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return UserMovieRating.objects.filter(user=self.request.user)

class MovieRatingLikeView(views.APIView):
    """Film değerlendirmesi beğenme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        try:
            rating = UserMovieRating.objects.get(pk=pk)
            if request.user in rating.likes.all():
                rating.likes.remove(request.user)
                return Response({'detail': 'Beğeni kaldırıldı.'})
            rating.likes.add(request.user)
            return Response({'detail': 'Değerlendirme beğenildi.'})
        except UserMovieRating.DoesNotExist:
            return Response(
                {'detail': 'Değerlendirme bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class WatchlistView(generics.ListAPIView):
    """İzleme listesi"""
    serializer_class = UserMovieWatchlistSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserMovieWatchlist.objects.filter(user=self.request.user)

class WatchlistAddView(views.APIView):
    """İzleme listesine film ekleme"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, movie_id):
        try:
            movie = Movie.objects.get(pk=movie_id)
            UserMovieWatchlist.objects.get_or_create(user=request.user, movie=movie)
            return Response({'detail': 'Film izleme listesine eklendi.'})
        except Movie.DoesNotExist:
            return Response(
                {'detail': 'Film bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class WatchlistRemoveView(views.APIView):
    """İzleme listesinden film çıkarma"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, movie_id):
        try:
            UserMovieWatchlist.objects.filter(
                user=request.user,
                movie_id=movie_id
            ).delete()
            return Response({'detail': 'Film izleme listesinden çıkarıldı.'})
        except Movie.DoesNotExist:
            return Response(
                {'detail': 'Film bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )

class MovieRecommendationsView(generics.ListAPIView):
    """Film önerileri"""
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # AI tabanlı film önerileri burada hesaplanacak
        return Movie.objects.all()[:10]

class UserRecommendationsView(generics.ListAPIView):
    """Kullanıcı önerileri"""
    serializer_class = MovieSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Kullanıcıya özel film önerileri burada hesaplanacak
        return Movie.objects.all()[:10]

class ListRecommendationsView(generics.ListAPIView):
    """Liste önerileri"""
    serializer_class = UserMovieListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Kullanıcıya özel liste önerileri burada hesaplanacak
        return UserMovieList.objects.filter(is_public=True)[:10] 