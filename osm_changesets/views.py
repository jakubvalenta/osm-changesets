import datetime
from dataclasses import dataclass
from typing import Optional

import requests
from celery.result import AsyncResult
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from django_ratelimit.decorators import ratelimit

from osm_changesets.forms import ChangesetQueryForm
from osm_changesets.tasks import render_svg


@dataclass
class Changeset:
    id: int
    comment: str
    created_at: datetime.datetime
    max_lat: float
    max_lon: float
    min_lat: float
    min_lon: float
    uid: int
    display_name: str
    query: "ChangesetQuery"

    @property
    def title(self) -> str:
        return self.comment or str(self.id)

    @property
    def url(self) -> str:
        if self.query.uid:
            return reverse("changeset-detail-by-uid", args=[self.query.uid, self.id])
        return reverse("changeset-detail-by-display-name", args=[self.query.display_name, self.id])

    @property
    def osm_url(self) -> str:
        return f"https://www.openstreetmap.org/changeset/{self.id}"


@dataclass
class ChangesetQuery:
    uid: Optional[int]
    display_name: Optional[str]

    def _call_api(self) -> dict:
        cache_key = (
            f"changesets-by-uid:{self.uid}"
            if self.uid
            else f"changesets-by-display-name:{self.display_name}"
        )
        data = cache.get(cache_key)
        if data is not None:
            return data

        r = requests.get(
            "https://api.openstreetmap.org/api/0.6/changesets",
            headers={"Accept": "application/json"},
            params=(
                {"user": str(self.uid)} if self.uid else {"display_name": str(self.display_name)}
            ),
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        cache.set(cache_key, data, 3600)
        return data

    def get_changesets(self) -> list[Changeset]:
        try:
            data = self._call_api()
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                raise Http404("User not found")
            raise err
        return [
            Changeset(
                id=int(item["id"]),
                comment=item.get("tags", {}).get("comment", ""),
                created_at=datetime.datetime.fromisoformat(item["created_at"]),
                max_lat=float(item["max_lat"]),
                max_lon=float(item["max_lon"]),
                min_lat=float(item["min_lat"]),
                min_lon=float(item["min_lon"]),
                uid=int(item["uid"]),
                display_name=item["user"],
                query=self,
            )
            for item in data.get("changesets", [])
        ]

    def get_changeset(self, id: int) -> Changeset | None:
        changesets = self.get_changesets()
        for changeset in changesets:
            if changeset.id == id:
                return changeset
        return None

    @property
    def title(self) -> str:
        return f"OpenStreetMap changesets by user {self.uid or self.display_name}"

    @property
    def url(self) -> str:
        if self.uid:
            return reverse("changeset-list-by-uid", args=[self.uid])
        return reverse("changeset-list-by-display-name", args=[self.display_name])

    @property
    def atom_url(self) -> str:
        if self.uid:
            return reverse("changeset-list-by-uid-atom", args=[self.uid])
        return reverse("changeset-list-by-display-name-atom", args=[self.display_name])

    @property
    def rss_url(self) -> str:
        if self.uid:
            return reverse("changeset-list-by-uid-rss", args=[self.uid])
        return reverse("changeset-list-by-display-name-rss", args=[self.display_name])


def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ChangesetQueryForm(request.POST)
        if form.is_valid():
            query = ChangesetQuery(
                uid=form.cleaned_data["uid"],
                display_name=form.cleaned_data["display_name"],
            )
            return redirect(query.url)
    else:
        form = ChangesetQueryForm()
    return render(request, "index.html", {"form": form})


def changeset_detail(
    request: HttpRequest,
    *,
    uid: Optional[int] = None,
    display_name: Optional[str] = None,
    id: int,
) -> HttpResponse:
    query = ChangesetQuery(uid=uid, display_name=display_name)
    changeset = query.get_changeset(id)
    if changeset is None:
        raise Http404("Changeset not found")
    return render(request, "changesets/detail.html", {"changeset": changeset})


def changeset_list(
    request: HttpRequest,
    *,
    uid: Optional[int] = None,
    display_name: Optional[str] = None,
) -> HttpResponse:
    query = ChangesetQuery(uid=uid, display_name=display_name)
    changesets = query.get_changesets()
    paginator = Paginator(changesets, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "changesets/list.html", {"page_obj": page_obj, "query": query})


@ratelimit(key="header:x-real-ip", rate="120/h", method=["GET"])
def changeset_svg(
    request: HttpRequest,
    uid: int,
    id: int,
) -> HttpResponse:
    query = ChangesetQuery(uid=uid, display_name=None)
    changeset = query.get_changeset(id)
    if changeset is None:
        raise Http404("Changeset not found")
    result_id_cache_key = f"changeset:{id}:result-id"
    result_id = cache.get(result_id_cache_key)
    if result_id is not None:
        result: AsyncResult = AsyncResult(result_id)
        if result.ready():
            svg = result.get()
            return HttpResponse(svg, content_type="image/svg+xml")
        result.forget()
    else:
        result = render_svg.delay(
            id,
            max_lat=changeset.max_lat,
            max_lon=changeset.max_lon,
            min_lat=changeset.min_lat,
            min_lon=changeset.min_lon,
        )
        cache.set(result_id_cache_key, result.id, 30 * 3600)
    return redirect(static("osm_changesets/rendering.svg"))


class RssChangesetsFeed(Feed):
    description_template = "changesets/description.html"

    def get_object(
        self,
        request: HttpRequest,
        *,
        uid: Optional[int] = None,
        display_name: Optional[str] = None,
    ) -> ChangesetQuery:
        return ChangesetQuery(uid=uid, display_name=display_name)

    def title(self, query: ChangesetQuery) -> str:
        return query.title

    def link(self, query: ChangesetQuery) -> str:
        return query.rss_url

    def items(self, query: ChangesetQuery) -> list[Changeset]:
        return query.get_changesets()[:10]

    def item_link(self, changeset: Changeset) -> str:
        return changeset.url

    def item_pubdate(self, changeset: Changeset) -> datetime.datetime:
        return changeset.created_at

    def item_title(self, changeset: Changeset) -> str:
        return changeset.title

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["changeset"] = context["obj"]
        return context


class AtomChangesetsFeed(RssChangesetsFeed):
    feed_type = Atom1Feed

    def link(self, query: ChangesetQuery) -> str:
        return query.atom_url
