from django.urls import path

from osm_changesets import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "changesets",
        views.ChangesetListView.as_view(),
        name="list",
    ),
    path(
        "changesets/<int:id>",
        views.ChangesetDetailView.as_view(),
        name="detail",
    ),
    path(
        "changesets/<int:id>.svg",
        views.changeset_svg,
        name="svg",
    ),
    path(
        "changesets.atom.xml",
        views.ChangesetAtomFeed(),
        name="atom",
    ),
    path(
        "changesets.rss.xml",
        views.ChangesetRssFeed(),
        name="rss",
    ),
]
