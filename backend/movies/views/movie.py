import rest_framework_filters as filters
from rest_framework import serializers, viewsets

from movies.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = (
            'title',
            'year',
            'genres',
            'avg_rating',
            'num_ratings',
            'imdb_url',
            'tmdb_url',
        )

    avg_rating = serializers.ReadOnlyField()
    num_ratings = serializers.ReadOnlyField()
    genres = serializers.ReadOnlyField(source='genre_names')


class MovieFilters(filters.FilterSet):
    class Meta:
        model = Movie
        fields = {}

    q = filters.CharFilter(method='filter_search')

    def filter_search(self, qs, name, value):
        return qs.search(value)


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Movie.objects.all()
            .annotate_ratings()
            .annotate_genre_names()
            .order_by('id')
    )
    serializer_class = MovieSerializer
    filterset_class = MovieFilters
