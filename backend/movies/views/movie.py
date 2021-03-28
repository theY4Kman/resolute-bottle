import rest_framework_filters as filters
from rest_framework import pagination, serializers, viewsets

from movies.models import Movie
from movies.search import parse_search_query


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = (
            'id',
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
        if not value:
            return qs

        return qs.search(parse_search_query(value), search_type='raw')


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Movie.objects.all()
            .annotate_ratings()
            .annotate_genre_names()
            .order_by('id')
    )
    serializer_class = MovieSerializer
    filterset_class = MovieFilters
    pagination_class = pagination.PageNumberPagination
