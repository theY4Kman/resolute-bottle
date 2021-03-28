import csv
import re
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Any, Iterable, TextIO, TypeVar
from zipfile import ZipFile, Path

import pytz
import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from tqdm import tqdm

from movies.models import Genre, Movie, Tag, User
from movies.models.rating import Rating

V = TypeVar('V')


def chunked(iterable: Iterable[V], chunk_size: int) -> Iterable[list[V]]:
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []

    if chunk:
        yield chunk


def read_csv_dicts(fp: TextIO, *,
                   show_progress: bool = True,
                   unit: str = 'it',
                   leave: bool = False,
                   ) -> Iterable[dict[str, Any]]:
    if show_progress:
        num_rows = sum(1 for _ in csv.reader(fp)) - 1  # account for header row
        fp.seek(0)
        return tqdm(csv.DictReader(fp), total=num_rows, unit=unit, leave=leave)
    else:
        return csv.DictReader(fp)


def parse_timestamp(ts_str: str) -> datetime:
    return datetime.utcfromtimestamp(int(ts_str)).replace(tzinfo=pytz.utc)


@dataclass
class MovieLensDataSet:
    links: TextIO = None
    movies: TextIO = None
    ratings: TextIO = None
    tags: TextIO = None


class Command(BaseCommand):
    help = 'Load in the MovieLens data set from file or the web'

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            'source', nargs='?',
            default='https://files.grouplens.org/datasets/movielens/ml-latest-small.zip',
        )
        parser.add_argument(
            '--no-verify', action='store_false', dest='verify', default=True,
            help='Skip SSL verification when downloading dataset from internet',
        )
        parser.add_argument(
            '--no-truncate', action='store_false', dest='truncate', default=True,
            help='Do not clear all rows from each table before loading dataset',
        )

    def handle(self, source: str, verify: bool, truncate: bool, **options):
        if source.startswith('http://') or source.startswith('https://'):
            res = requests.get(source, verify=verify, stream=True)
            zip_source = BytesIO()
            for chunk in res.iter_content(1024):
                zip_source.write(chunk)
        else:
            zip_source = source

        zipf = ZipFile(zip_source, mode='r')
        dataset = self.extract_csvs(zipf)

        # We only truncate after the dataset has been successfully opened
        if truncate:
            with connection.cursor() as cursor:
                for model in Genre, Movie, Rating, Tag, User:
                    cursor.execute(f'TRUNCATE TABLE {model._meta.db_table} RESTART IDENTITY CASCADE;')

        self.import_dataset(dataset)

    def extract_csvs(self, zipf: ZipFile) -> MovieLensDataSet:
        dataset = MovieLensDataSet()
        valid_stems = set(dataset.__annotations__)

        for info in zipf.filelist:
            path = Path(zipf, at=info.filename)

            if path.name.endswith('.csv') and (stem := path.name[:-len('.csv')]) in valid_stems:
                setattr(dataset, stem, path.open('r', encoding='utf-8'))

        return dataset

    def import_dataset(self, dataset: MovieLensDataSet):
        genres: dict[str, Genre] = {
            genre.name: genre
            for genre in Genre.objects.all()
        }

        movies_added = 0
        genres_added = 0
        users_added = 0
        ratings_added = 0
        tags_added = 0

        for raw_movies in chunked(read_csv_dicts(dataset.movies, unit='movie'), 500):
            movies = []
            genres_encountered = set()
            for raw_movie in raw_movies:
                raw_title = raw_movie['title'].strip()
                if match := re.match(r'^(.+) \((\d{4})\)$', raw_title):
                    title, year = match.groups()
                else:
                    title, year = raw_title, None

                movie_id = int(raw_movie['movieId'])
                movie_genres = set(raw_movie['genres'].split('|'))
                genres_encountered |= movie_genres

                movie = Movie(id=movie_id, title=title, year=year)
                movie._raw_genres = movie_genres

                movies.append(movie)

            movies_added += len(Movie.objects.bulk_create(movies, ignore_conflicts=True))

            if missing_genre_names := genres_encountered - set(genres):
                missing_genres: list[Genre] = []

                for genre_name in missing_genre_names:
                    genre = Genre(name=genre_name)
                    genres[genre_name] = genre
                    missing_genres.append(genre)

                genres_added += len(Genre.objects.bulk_create(missing_genres))

            movie_genres = [
                Movie.genres.through(movie=movie, genre=genres[genre_name])
                for movie in movies
                for genre_name in movie._raw_genres
            ]
            Movie.genres.through.objects.bulk_create(movie_genres)

        for raw_links in chunked(read_csv_dicts(dataset.links, unit='link'), 1000):
            movie_links = [
                Movie(id=raw_link['movieId'],
                      imdb_id=raw_link['imdbId'], tmdb_id=raw_link['tmdbId'])
                for raw_link in raw_links
            ]
            Movie.objects.bulk_update(movie_links, ['imdb_id', 'tmdb_id'])

        for raw_ratings in chunked(read_csv_dicts(dataset.ratings, unit='rating'), 1000):
            user_ids = set()
            ratings = []
            for raw_rating in raw_ratings:
                user_ids.add(raw_rating['userId'])
                ratings.append(Rating(
                    user_id=raw_rating['userId'],
                    movie_id=raw_rating['movieId'],
                    rating=raw_rating['rating'],
                    timestamp=parse_timestamp(raw_rating['timestamp']),
                ))

            users = [User(id=user_id) for user_id in user_ids]
            users_added += len(User.objects.bulk_create(users, ignore_conflicts=True))

            ratings_added += len(Rating.objects.bulk_create(ratings))

        for raw_tags in chunked(read_csv_dicts(dataset.tags, unit='tag'), 1000):
            user_ids = set()
            tags = []
            for raw_tag in raw_tags:
                user_ids.add(raw_tag['userId'])
                tags.append(Tag(
                    user_id=raw_tag['userId'],
                    movie_id=raw_tag['movieId'],
                    name=raw_tag['tag'],
                    timestamp=parse_timestamp(raw_tag['timestamp']),
                ))

            users = [User(id=user_id) for user_id in user_ids]
            users_added += len(User.objects.bulk_create(users, ignore_conflicts=True))

            tags_added += len(Tag.objects.bulk_create(tags))

        self.stdout.write(f'Successfully added {movies_added} movies, {genres_added} genres, '
                          f'{users_added} users, {ratings_added} ratings, and {tags_added} tags')
