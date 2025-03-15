from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User

class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    imdb_id = models.CharField(max_length=20, null=True, blank=True)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, null=True, blank=True)
    vote_average = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)
    overview = models.TextField(null=True, blank=True)
    homepage = models.URLField(null=True, blank=True)
    popularity = models.FloatField(default=0)
    original_language = models.CharField(max_length=10, default='Unknown')
    poster = models.URLField(null=True, blank=True)
    backdrop = models.URLField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    budget = models.BigIntegerField(default=0)
    revenue = models.BigIntegerField(default=0)
    status = models.CharField(max_length=50, null=True, blank=True)
    video = models.BooleanField(default=False)
    tagline = models.CharField(max_length=255, null=True, blank=True)

    genres = models.ManyToManyField(Genre, related_name='movies')

    def __str__(self):
        return self.title

class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    gender = models.IntegerField(null=True, blank=True)
    profile_path = models.URLField(null=True, blank=True)
    known_for_department = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='cast')
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    character_name = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(default=999)
    popularity = models.FloatField(default=0)

    class Meta:
        unique_together = ('movie', 'person')

    def __str__(self):
        return f"{self.person.name} as {self.character_name} in {self.movie.title}"

class Crew(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='crew')
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, null=True, blank=True)
    job = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('movie', 'person', 'job')

    def __str__(self):
        return f"{self.person.name} ({self.job}) in {self.movie.title}"

class Director(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='directors')
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'person')

    def __str__(self):
        return f"{self.person.name} - {self.movie.title}"
#class Genre(models.Model):
#    """Film/Dizi türleri"""
#    name = models.CharField(_('Tür Adı'), max_length=100)
#    description = models.TextField(_('Açıklama'), blank=True)
#    
#    class Meta:
#        verbose_name = _('Tür')
#        verbose_name_plural = _('Türler')
#        
#    def __str__(self):
#        return self.name
#
#class Person(models.Model):
#    """Oyuncu, yönetmen, senarist vb."""
#    name = models.CharField(_('Ad'), max_length=255)
#    bio = models.TextField(_('Biyografi'), blank=True)
#    photo = models.ImageField(_('Fotoğraf'), upload_to='people/', null=True, blank=True)
#    birth_date = models.DateField(_('Doğum Tarihi'), null=True, blank=True)
#    death_date = models.DateField(_('Ölüm Tarihi'), null=True, blank=True)
#    imdb_id = models.CharField(_('IMDB ID'), max_length=50, blank=True)
#    tmdb_id = models.IntegerField(_('TMDB ID'), null=True, blank=True)
#    
#    class Meta:
#        verbose_name = _('Kişi')
#        verbose_name_plural = _('Kişiler')
#        
#    def __str__(self):
#        return self.name
#
#class Movie(models.Model):
#    """Film modeli"""
#    title = models.CharField(_('Başlık'), max_length=255)
#    original_title = models.CharField(_('Orijinal Başlık'), max_length=255)
#    overview = models.TextField(_('Özet'))
#    poster = models.ImageField(_('Afiş'), upload_to='movies/posters/', null=True)
#    backdrop = models.ImageField(_('Arka Plan'), upload_to='movies/backdrops/', null=True)
#    release_date = models.DateField(_('Yayın Tarihi'))
#    runtime = models.IntegerField(_('Süre (dakika)'))
#    budget = models.BigIntegerField(_('Bütçe'), null=True, blank=True)
#    revenue = models.BigIntegerField(_('Hasılat'), null=True, blank=True)
#    imdb_id = models.CharField(_('IMDB ID'), max_length=50, blank=True)
#    tmdb_id = models.IntegerField(_('TMDB ID'), null=True, blank=True)
#    genres = models.ManyToManyField(Genre, related_name='movies', verbose_name=_('Türler'))
#    cast = models.ManyToManyField(Person, through='MovieCast', related_name='movies_acted')
#    crew = models.ManyToManyField(Person, through='MovieCrew', related_name='movies_worked')
#    
#    #fragman linkleri listesi olacak
#    # trailer = models.URLField(_('Fragman'), blank=True)
#    class Meta:
#        verbose_name = _('Film')
#        verbose_name_plural = _('Filmler')
#        
#    def __str__(self):
#        return self.title
#
#class MovieCast(models.Model):
#    """Film oyuncu kadrosu"""
#    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#    person = models.ForeignKey(Person, on_delete=models.CASCADE)
#    character = models.CharField(_('Karakter'), max_length=255)
#    order = models.IntegerField(_('Sıra'))
#    
#    class Meta:
#        verbose_name = _('Film Oyuncusu')
#        verbose_name_plural = _('Film Oyuncuları')
#        ordering = ['order']
#
#class MovieCrew(models.Model):
#    """Film ekibi"""
#    DEPARTMENT_CHOICES = [
#        ('directing', _('Yönetmen')),
#        ('writing', _('Senarist')),
#        ('production', _('Yapımcı')),
#        ('camera', _('Görüntü Yönetmeni')),
#        ('editing', _('Kurgu')),
#        ('sound', _('Ses')),
#        ('art', _('Sanat')),
#        ('costume', _('Kostüm')),
#        ('other', _('Diğer')),
#    ]
#    
#    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#    person = models.ForeignKey(Person, on_delete=models.CASCADE)
#    department = models.CharField(_('Departman'), max_length=50, choices=DEPARTMENT_CHOICES)
#    job = models.CharField(_('Görev'), max_length=255)
#    
#    class Meta:
#        verbose_name = _('Film Ekibi')
#        verbose_name_plural = _('Film Ekibi')

class UserMovieList(models.Model):
    """Kullanıcı film listeleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_lists')
    name = models.CharField(_('Liste Adı'), max_length=255)
    description = models.TextField(_('Açıklama'), blank=True)
    is_public = models.BooleanField(_('Herkese Açık'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movies = models.ManyToManyField(Movie, through='UserMovieListItem')
    
    class Meta:
        verbose_name = _('Film Listesi')
        verbose_name_plural = _('Film Listeleri')

class UserMovieListItem(models.Model):
    """Film listesi öğeleri"""
    movie_list = models.ForeignKey(UserMovieList, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    notes = models.TextField(_('Notlar'), blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(_('Sıra'))
    
    class Meta:
        verbose_name = _('Liste Öğesi')
        verbose_name_plural = _('Liste Öğeleri')
        ordering = ['order']

class UserMovieRating(models.Model):
    """Kullanıcı film değerlendirmeleri"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
    rating = models.DecimalField(_('Puan'), max_digits=3, decimal_places=1)
    review = models.TextField(_('İnceleme'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_movie_ratings')
    
    class Meta:
        verbose_name = _('Film Değerlendirmesi')
        verbose_name_plural = _('Film Değerlendirmeleri')
        unique_together = ('user', 'movie')

class UserMovieWatchlist(models.Model):
    """İzleme listesi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(_('Notlar'), blank=True)
    
    class Meta:
        verbose_name = _('İzleme Listesi')
        verbose_name_plural = _('İzleme Listeleri')
        unique_together = ('user', 'movie') 
