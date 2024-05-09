from django.urls import path

from osm_pretty_rss.feeds import AtomUserChangesetsFeed, RssUserChangesetsFeed

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("feeds/<int:uid>.atom", AtomUserChangesetsFeed(), name="feed-atom"),
    path("feeds/<int:uid>.rss", RssUserChangesetsFeed(), name="feed-rss"),
]
