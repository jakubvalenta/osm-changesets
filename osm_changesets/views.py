import datetime

from django.contrib.syndication.views import Feed
from django.core.exceptions import BadRequest
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.feedgenerator import Atom1Feed, SyndicationFeed
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django_ratelimit.decorators import ratelimit

from osm_changesets.forms import ChangesetsForm
from osm_changesets.models import Changeset
from osm_changesets.tasks import get_svg

PAGE_SIZE = 10
FEED_LIMIT = 10


def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ChangesetsForm(request.POST)
        if form.is_valid():
            return redirect(form.list_url)
    else:
        form = ChangesetsForm()
    return render(request, "index.html", {"form": form})


class ChangesetDetailView(DetailView):
    model = Changeset
    context_object_name = "changeset"
    pk_url_kwarg = "id"
    template_name = "changesets/detail.html"

    form: ChangesetsForm

    @method_decorator(ratelimit(key="header:x-real-ip", rate="600/h", method=["GET"]))
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)

    def get_queryset(self) -> QuerySet[Changeset]:
        self.form = ChangesetsForm(self.request.GET)
        if not self.form.is_valid():
            raise BadRequest("Invalid parameters")
        return super().get_queryset()

    def get_object(self, queryset: QuerySet | None = None) -> Changeset:
        changeset: Changeset = super().get_object(queryset)
        changeset.render()
        return changeset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context


class ChangesetListView(ListView):
    model = Changeset
    context_object_name = "changesets"
    paginate_by = PAGE_SIZE
    template_name = "changesets/list.html"

    form: ChangesetsForm

    @method_decorator(ratelimit(key="header:x-real-ip", rate="60/h", method=["GET"]))
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)

    def get_queryset(self) -> QuerySet[Changeset]:
        params = self.request.GET.copy()
        params.pop(self.page_kwarg, None)
        self.form = ChangesetsForm(params)
        if not self.form.is_valid():
            raise BadRequest("Invalid parameters")
        self.form.download_changesets()
        return self.form.get_changesets()

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        context["FEED_LIMIT"] = FEED_LIMIT
        for changeset in context["changesets"]:
            changeset.render()
        return context


def changeset_svg(request: HttpRequest, id: int) -> HttpResponse:
    svg = get_svg(id)
    if svg is None:
        return HttpResponse("Waiting for SVG rendering to complete", status=503)
    return HttpResponse(svg, content_type="image/svg+xml")


class ChangesetRssFeed(Feed):
    description_template = "changesets/description.html"

    @method_decorator(ratelimit(key="header:x-real-ip", rate="60/h", method=["GET"]))
    def get_object(self, request: HttpRequest) -> ChangesetsForm:
        form = ChangesetsForm(request.GET)
        if not form.is_valid():
            raise BadRequest("Invalid parameters")
        form.download_changesets()
        return form

    def items(self, form: ChangesetsForm) -> QuerySet[Changeset]:
        changesets = form.get_changesets()[:FEED_LIMIT]
        for changeset in changesets:
            changeset.render()
        return changesets

    def title(self, form: ChangesetsForm) -> str:
        return form.title

    def link(self, form: ChangesetsForm) -> str:
        return form.rss_url

    def changeset_pubdate(self, changeset: Changeset) -> datetime.datetime:
        return changeset.created_at

    def changeset_title(self, changeset: Changeset) -> str:
        return changeset.title

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["changeset"] = context["obj"]
        return context


class ChangesetAtomFeed(ChangesetRssFeed):
    feed_type: type[SyndicationFeed] = Atom1Feed

    def link(self, form: ChangesetsForm) -> str:
        return form.atom_url
