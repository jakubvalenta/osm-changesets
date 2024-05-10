from django.shortcuts import redirect, render
from django.views import generic

from osm_pretty_rss.forms import UserForm
from osm_pretty_rss.models import User


def index(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            uid = form.cleaned_data["uid"]
            user_name = form.cleaned_data["user_name"]
            user = User.objects.create(uid=uid, user_name=user_name)
            user.refresh()
            return redirect("user-detail", uid=uid)
    else:
        form = UserForm()
    return render(request, "index.html", {"form": form})


class UserDetailView(generic.DetailView):
    model = User
    template_name = "users/detail.html"
