from django.db import models

from ._base import BaseModel


class Rating(BaseModel):
    rating = models.FloatField(help_text='From 0 to 5, in 0.5 increments')
    timestamp = models.DateTimeField()

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='ratings')

    def __str__(self):
        return self.to_text()

    # NOTE: circles chosen by default, instead of stars, because the half-filled star doesn't
    #       render with my system fonts
    def to_text(self, filled_char: str = '●', half_char: str = '◐', empty_char: str = '○') -> str:
        steps = int(self.rating * 10) / 5
        filled, half = divmod(steps, 2)
        filled //= 2
        empty = 5 - (filled + half)
        return filled_char * filled + half_char * half + empty_char * empty
