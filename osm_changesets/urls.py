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
    path("changesets-by-display-name/<str:display_name>", views.redirect_list_by_display_name_view),
    path("changesets-by-uid/<int:uid>", views.redirect_list_by_uid_view),
    path(
        "changesets-by-display-name/<str:display_name>/<int:id>",
        views.redirect_detail_by_display_name_view,
    ),
    path("changesets-by-uid/<int:uid>/<int:id>", views.redirect_detail_by_uid_view),
    path("changesets-by-uid/<int:uid>/<int:id>.svg", views.redirect_svg_view),
    path(
        "changesets-by-display-name/<str:display_name>/atom.xml",
        views.redirect_atom_feed_by_display_name_view,
    ),
    path("changesets-by-uid/<int:uid>/atom.xml", views.redirect_atom_feed_by_uid_view),
    path(
        "changesets-by-display-name/<str:display_name>/rss.xml",
        views.redirect_rss_feed_by_display_name_view,
    ),
    path("changesets-by-uid/<int:uid>/rss.xml", views.redirect_rss_feed_by_uid_view),
]
