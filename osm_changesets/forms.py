import datetime
from urllib.parse import urlencode

import requests
from django import forms
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import Http404
from django.urls import reverse

# from osm_changesets.managers import ChangesetManager
from osm_changesets.models import Changeset


class ChangesetsForm(forms.Form):
    display_name = forms.CharField(
        label="or display name",
        widget=forms.TextInput(attrs={"placeholder": "Jakub Valenta"}),
        required=False,
    )
    uid = forms.IntegerField(
        label="Enter user id",
        widget=forms.TextInput(attrs={"placeholder": "4151758"}),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        display_name = cleaned_data.get("display_name")
        uid = cleaned_data.get("uid")
        if not display_name and not uid:
            raise ValidationError("Enter user id or display name.")
        if display_name and uid:
            raise ValidationError("Enter only one of user id or display name.")

    @property
    def title(self) -> str:
        return "OpenStreetMap changesets by user %s" % (
            self.cleaned_data["display_name"] or self.cleaned_data["uid"]
        )

    @property
    def query_string(self) -> str:
        display_name = self.cleaned_data["display_name"]
        uid = self.cleaned_data["uid"]
        return urlencode({"display_name": display_name} if display_name else {"uid": uid})

    @property
    def atom_url(self) -> str:
        return reverse("atom") + "?" + self.query_string

    @property
    def rss_url(self) -> str:
        return reverse("rss") + "?" + self.query_string

    @property
    def list_url(self) -> str:
        return reverse("list") + "?" + self.query_string

    def download_changesets(self):
        try:
            data = self._call_api()
        except requests.HTTPError as err:
            if err.response.status_code == 404:
                raise Http404("User not found")
            raise err
        Changeset.objects.bulk_create(
            (
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
                )
                for item in data.get("changesets", [])
            ),
            ignore_conflicts=True,
        )

    def get_changesets(self) -> QuerySet[Changeset, Changeset]:
        display_name = self.cleaned_data["display_name"]
        uid = self.cleaned_data["uid"]
        return Changeset.objects.filter(Q(display_name=display_name) | Q(uid=uid))

    def _call_api(self) -> dict:
        display_name = self.cleaned_data["display_name"]
        uid = self.cleaned_data["uid"]
        cache_key = (
            f"api:changesets:display-name:{display_name}"
            if display_name
            else f"api:changesets:uid:{uid}"
        )
        data = cache.get(cache_key)
        if data is not None:
            return data

        r = requests.get(
            "https://api.openstreetmap.org/api/0.6/changesets",
            headers={"Accept": "application/json"},
            params=({"display_name": display_name} if display_name else {"user": str(uid)}),
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        cache.set(cache_key, data, 3600)
        return data
