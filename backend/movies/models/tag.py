from django.db import models
from django.db.models.functions import Upper

from ._base import BaseModel


class Tag(BaseModel):
    # NOTE: on Postgres, all string fields are handled the same, and "max length"
    #       is simply a constraint.
    name = models.CharField(max_length=1024)
    timestamp = models.DateTimeField()

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='tags')
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, related_name='tags')

    class Meta:
        indexes = (
            # Improves performance of case-insensitive queries
            #  (Django uses UPPER() to perform iexact/icontains queries)
            models.Index(Upper('name'),
                         name='tag_name_case_insensitive'),
        )

    def __str__(self):
        return self.name

    def _repr_str(self) -> str:
        return f'"{self.name}" on "{self.movie}" by {self.user}'
