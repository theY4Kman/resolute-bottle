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


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.annotate_ratings().annotate_genre_names()
    serializer_class = MovieSerializer
