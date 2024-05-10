from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from osm_pretty_rss.feeds import AtomUserChangesetsFeed, RssUserChangesetsFeed

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("users/<int:pk>", views.UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/feed.atom", AtomUserChangesetsFeed(), name="user-feed-atom"),
    path("users/<int:pk>/feed.rss", RssUserChangesetsFeed(), name="user-feed-rss"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
