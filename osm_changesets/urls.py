from django.urls import path

from osm_changesets import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "changesets-by-uid/<int:uid>",
        views.changeset_list,
        name="changeset-list-by-uid",
    ),
    path(
        "changesets-by-display-name/<str:display_name>",
        views.changeset_list,
        name="changeset-list-by-display-name",
    ),
    path(
        "changesets-by-uid/<int:uid>/<int:id>",
        views.changeset_detail,
        name="changeset-detail-by-uid",
    ),
    path(
        "changesets-by-display-name/<str:display_name>/<int:id>",
        views.changeset_detail,
        name="changeset-detail-by-display-name",
    ),
    path(
        "changesets-by-uid/<int:uid>/atom.xml",
        views.AtomChangesetsFeed(),
        name="changeset-list-by-uid-atom",
    ),
    path(
        "changesets-by-display-name/<str:display_name>/atom.xml",
        views.AtomChangesetsFeed(),
        name="changeset-list-by-display-name-atom",
    ),
    path(
        "changesets-by-uid/<int:uid>/rss.xml",
        views.RssChangesetsFeed(),
        name="changeset-list-by-uid-rss",
    ),
    path(
        "changesets-by-display-name/<str:display_name>/rss.xml",
        views.RssChangesetsFeed(),
        name="changeset-list-by-display-name-rss",
    ),
]
