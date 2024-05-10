import datetime

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed

from osm_pretty_rss.models import Changeset, User


class RssUserChangesetsFeed(Feed):
    def get_object(self, request, pk: int) -> User:
        return User.objects.get(uid=pk)

    def title(self, user: User) -> str:
        return user.title

    def link(self, user: User) -> str:
        return user.feed_rss_url

    def items(self, user: User) -> list[Changeset]:  # TODO Return type
        return user.changesets.all()

    def item_enclosure_url(self, changeset: Changeset) -> str:
        return changeset.svg.url  # TODO Absolute URL

    def item_enclosure_mime_type(self, changeset: Changeset) -> str:
        return "image/svg+xml"

    def item_enclosure_length(self, changeset: Changeset) -> str:
        return changeset.svg.size

    def item_link(self, changeset: Changeset) -> str:
        return changeset.osm_url

    def item_pubdate(self, changeset: Changeset) -> datetime.datetime:
        return changeset.created_at

    def item_title(self, changeset: Changeset) -> str:
        return changeset.title


class AtomUserChangesetsFeed(RssUserChangesetsFeed):
    feed_type = Atom1Feed

    def link(self, user: User) -> str:
        return user.feed_atom_url
