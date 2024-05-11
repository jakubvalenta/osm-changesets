import datetime
import io
from pathlib import Path
from typing import IO, Dict

import requests
import staticmaps
from django.core.files.base import File
from django.db import models, transaction
from django.urls import reverse


def render_changeset_svg(id: int) -> IO:
    r = requests.get(
        f"https://api.openstreetmap.org/api/0.6/changeset/{id}",
        headers={"Accept": "application/json"},
    )
    r.raise_for_status()
    data = r.json()

    max_lat = float(data["elements"][0]["maxlat"])
    max_lon = float(data["elements"][0]["maxlon"])
    min_lat = float(data["elements"][0]["minlat"])
    min_lon = float(data["elements"][0]["minlon"])

    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OSM)

    if min_lat == max_lat and min_lon == max_lon:
        context.add_object(
            staticmaps.Marker(staticmaps.create_latlng(min_lat, min_lon))
        )
    else:
        context.add_object(
            staticmaps.Area(
                [
                    staticmaps.create_latlng(lat, lng)
                    for lat, lng in [
                        (min_lat, min_lon),
                        (min_lat, max_lon),
                        (max_lat, max_lon),
                        (max_lat, min_lon),
                    ]
                ],
            )
        )

    drawing = context.render_svg(800, 500)
    f = io.StringIO()
    drawing.write(f)
    return f


def changeset_upload_to(instance: "Changeset", filename: str) -> str:
    return str(Path("changesets") / f"{instance.id}.svg")


class User(models.Model):
    uid = models.IntegerField(primary_key=True)

    MAX_CHANGESETS: int = 10

    def refresh(self) -> None:
        r = requests.get(
            "https://api.openstreetmap.org/api/0.6/changesets",
            headers={"Accept": "application/json"},
            params={"user": self.uid},
        )
        r.raise_for_status()
        data = r.json()

        old_changesets: Dict[int, Changeset] = {
            changeset.id: changeset
            for changeset in self.changesets.filter().order_by("created_at")
        }
        new_changesets: Dict[int, Changeset] = {}
        for item in data.get("changesets", [])[: self.MAX_CHANGESETS]:
            id = int(item["id"])
            if id in old_changesets:
                new_changesets[id] = old_changesets[id]
            else:
                new_changesets[id] = Changeset(
                    id=id,
                    comment=item.get("tags", {}).get("comment", ""),
                    created_at=datetime.datetime.fromisoformat(item["created_at"]),
                    max_lat=int(item["max_lat"]),
                    max_lon=int(item["max_lon"]),
                    min_lat=int(item["min_lat"]),
                    min_lon=int(item["min_lon"]),
                    user=self,
                )

        with transaction.atomic():
            for id, changeset in old_changesets.items():
                if id not in new_changesets:
                    changeset.delete()
            for id, changeset in new_changesets.items():
                if id not in old_changesets:
                    changeset.svg.save("ignored", File(render_changeset_svg(id)))

    @property
    def title(self) -> str:
        return f"OpenStreetMap changesets by user {self.uid}"

    @property
    def feed_rss_url(self) -> str:
        return reverse("user-feed-rss", kwargs={"pk": self.uid})

    @property
    def feed_atom_url(self) -> str:
        return reverse("user-feed-atom", kwargs={"pk": self.uid})


class Changeset(models.Model):
    id = models.IntegerField(primary_key=True)
    comment = models.TextField()
    created_at = models.DateTimeField()
    max_lat = models.FloatField()
    max_lon = models.FloatField()
    min_lat = models.FloatField()
    min_lon = models.FloatField()
    svg = models.FileField(upload_to=changeset_upload_to)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="changesets")

    class Meta:
        ordering = ["-created_at"]

    @property
    def title(self) -> str:
        return self.comment or str(self.id)

    @property
    def osm_url(self) -> str:
        return f"https://www.openstreetmap.org/changeset/{self.id}"
