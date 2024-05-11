from django import forms


class CreateUserForm(forms.Form):
    uid = forms.IntegerField(
        label="Enter a user id",
        widget=forms.TextInput(attrs={"placeholder": "4151758"}),
    )


class FindUserForm(forms.Form):
    user_name = forms.CharField(
        label="Or find a user by their name",
        widget=forms.TextInput(attrs={"placeholder": "Jakub Valenta"}),
    )
