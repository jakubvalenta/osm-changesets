from urllib.parse import urlencode

from django.db import models
from django.urls import reverse

from osm_changesets.tasks import get_svg, render_svg


class Changeset(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    comment = models.TextField()
    created_at = models.DateTimeField()
    max_lat = models.FloatField()
    max_lon = models.FloatField()
    min_lat = models.FloatField()
    min_lon = models.FloatField()
    uid = models.PositiveIntegerField(null=True)
    display_name = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.id)

    def get_absolute_url(self) -> str:
        return reverse("detail", args=[self.id]) + "?" + urlencode({"uid": self.uid})

    def render(self) -> None:
        if get_svg(self.id) is None:
            render_svg.delay(
                self.id,
                max_lat=self.max_lat,
                max_lon=self.max_lon,
                min_lat=self.min_lat,
                min_lon=self.min_lon,
            )

    @property
    def title(self) -> str:
        return self.comment or str(self.id)

    @property
    def osm_url(self) -> str:
        return f"https://www.openstreetmap.org/changeset/{self.id}"
