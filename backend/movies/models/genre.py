from django.db import models

from ._base import BaseModel


class Genre(BaseModel):
    # NOTE: on Postgres, all string fields are handled the same, and "max length"
    #       is simply a constraint.
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name
