from django.db import models

from ._base import BaseModel


class User(BaseModel):
    id = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        return f'User {self.id}'
