import datetime
from dataclasses import dataclass

import requests
from django.contrib.syndication.views import Feed
from django.shortcuts import render
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed


@dataclass
class Changeset:
    comment: str
    created_at: datetime.datetime
    id: int
    max_lat: float
    max_lon: float
    min_lat: float
    min_lon: float


@dataclass
class User:
    uid: int
    changesets: list[Changeset]


class RssUserChangesetsFeed(Feed):
    def get_object(self, request, uid) -> User:
        r = requests.get(
            "https://api.openstreetmap.org/api/0.6/changesets",
            headers={"Accept": "application/json"},
            params={"user": uid},
        )
        r.raise_for_status()
        data = r.json()
        print(data)
        changesets = [
            Changeset(
                comment=item.get("tags", {}).get("comment", ""),
                created_at=datetime.datetime.fromisoformat(item["created_at"]),
                id=int(item["id"]),
                max_lat=float(item["max_lat"]),
                max_lon=float(item["max_lon"]),
                min_lat=float(item["min_lat"]),
                min_lon=float(item["min_lon"]),
            )
            for item in data.get("changesets", [])
        ]
        return User(uid=uid, changesets=changesets)

    def title(self, user: User) -> str:
        return f"OpenStreetMap changesets by user {user.uid}"

    def link(self, user: User) -> str:
        return reverse("feed-rss", kwargs={"uid": user.uid})

    def items(self, user: User) -> list[Changeset]:
        return user.changesets

    def item_description(self, changeset: Changeset) -> str:
        return str(changeset)

    def item_link(self, changeset: Changeset) -> str:
        return f"https://www.openstreetmap.org/changeset/{changeset.id}"

    def item_title(self, changeset: Changeset) -> str:
        return f"Changeset {changeset.id}" + (
            f": {changeset.comment}" if changeset.comment else ""
        )


class AtomUserChangesetsFeed(RssUserChangesetsFeed):
    feed_type = Atom1Feed

    def link(self, user: User) -> str:
        return reverse("feed-atom", kwargs={"uid": user.uid})
