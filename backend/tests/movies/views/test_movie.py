from typing import Any

import pytest
from django.db.models import Avg
from pytest_drf import Returns200, UsesDetailEndpoint, UsesGetMethod, UsesListEndpoint, ViewSetTest
from pytest_drf.util import pluralized, url_for
from pytest_lambda import lambda_fixture

from movies.models import Movie


def express_movie(movie: Movie) -> dict[str, Any]:
    return {
        'title': movie.title,
        'year': movie.year,
        'genres': list(movie.genres.values_list('name', flat=True)),
        'avg_rating': movie.ratings.aggregate(avg=Avg('rating'))['avg'],
        'num_ratings': movie.ratings.count(),
        'imdb_url': movie.imdb_url,
        'tmdb_url': movie.tmdb_url,
    }


express_movies = pluralized(express_movie)


@pytest.mark.django_db
class DescribeMovieViewSet(ViewSetTest):
    list_url = lambda_fixture(lambda: url_for('movies-list'))
    detail_url = lambda_fixture(lambda movie: url_for('movies-detail', pk=movie.pk))


    class DescribeList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        movies = lambda_fixture(lambda: Movie.objects.bulk_create([
            Movie(title="Alfred Hitchcock's The Byrds: A Biopic", year=1975),
            Movie(title='Forty-Two Monkeys', year=1997),
        ]))

        def it_returns_movies(self, movies, json):
            expected = express_movies(movies)
            actual = json
            assert expected == actual


    class DescribeRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        movie = lambda_fixture(lambda: Movie.objects.create(
            title='The Muffin Man',
            year=2038,
        ))

        def it_returns_movie(self, movie, json):
            expected = express_movie(movie)
            actual = json
            assert expected == actual
