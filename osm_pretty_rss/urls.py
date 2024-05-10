from django.urls import path

from osm_pretty_rss.feeds import AtomUserChangesetsFeed, RssUserChangesetsFeed

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("changesets/<int:id>.png", views.changeset_png, name="changeset-png"),
    path("changesets/<int:id>.svg", views.changeset_svg, name="changeset-svg"),
    path("feeds/<int:uid>.atom", AtomUserChangesetsFeed(), name="feed-atom"),
    path("feeds/<int:uid>.rss", RssUserChangesetsFeed(), name="feed-rss"),
]
