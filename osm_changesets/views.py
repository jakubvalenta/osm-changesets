from dataclasses import dataclass

import requests
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import generic

from osm_changesets.forms import CreateUserForm, FindUserForm
from osm_changesets.models import Changeset, User


@dataclass
class FoundUser:
    uid: int
    user_names: list[str]


def create_user(uid: int) -> None:
    user = User(uid=uid)
    user.save()
    user.refresh()


def find_users(user_name: str) -> list[FoundUser]:
    r = requests.get(
        "https://whosthat.osmz.ru/whosthat/whosthat.php",
        params={"name": user_name, "action": "names"},
    )
    r.raise_for_status()
    data = r.json()
    return [
        FoundUser(uid=int(item["id"]), user_names=[str(x) for x in item["names"]])
        for item in data
    ]


def index(request: HttpRequest) -> HttpResponse:
    create_form = CreateUserForm()
    find_form = FindUserForm()
    found_users: list[FoundUser] = []
    if request.method == "POST":
        if "find" in request.POST:
            find_form = FindUserForm(request.POST)
            if find_form.is_valid():
                user_name = find_form.cleaned_data["user_name"]
                found_users = find_users(user_name)
        else:
            create_form = CreateUserForm(request.POST)
            if create_form.is_valid():
                uid = create_form.cleaned_data["uid"]
                create_user(uid)
                return redirect("user-detail", pk=uid)
    return render(
        request,
        "index.html",
        {
            "create_form": create_form,
            "find_form": find_form,
            "found_users": found_users,
        },
    )


class UserDetailView(generic.DetailView):
    model = User
    template_name = "users/detail.html"

    def get_context_data(self, **kwargs) -> dict:
        queryset = self.object.changesets.all()
        paginator = Paginator(queryset, User.MAX_CHANGESETS)
        page = self.request.GET.get("page")
        page_obj = paginator.get_page(page)
        context = super().get_context_data(**kwargs)
        context["page_obj"] = page_obj
        return context


class ChangesetDetailView(generic.DetailView):
    model = Changeset
    template_name = "changesets/detail.html"
