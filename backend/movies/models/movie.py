from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db import models

from ._base import BaseModel


MOVIE_TITLE_SEARCH_VECTOR = SearchVector('title', config='english')


class MovieQuerySet(models.QuerySet):
    def search(self, query: str, phrase: bool = True) -> 'MovieQuerySet':
        qs = self
        qs = qs.annotate(title_vector=MOVIE_TITLE_SEARCH_VECTOR)
        qs = qs.filter(
            title_vector=SearchQuery(
                query,
                config=MOVIE_TITLE_SEARCH_VECTOR.config,
                search_type='phrase' if phrase else 'plain',
            ),
        )
        return qs


class Movie(BaseModel):
    # NOTE: on Postgres, all string fields are handled the same, and "max length"
    #       is simply a constraint.
    title = models.CharField(max_length=1024)
    year = models.PositiveIntegerField(blank=True, null=True)
    genres = models.ManyToManyField('Genre', related_name='movies', blank=True)

    objects = MovieQuerySet.as_manager()

    class Meta:
        indexes = (
            GinIndex(MOVIE_TITLE_SEARCH_VECTOR,
                     name='movie_title_search'),
        )

    def __str__(self):
        if self.year is None:
            return self.title
        else:
            return f'{self.title} ({self.year})'
