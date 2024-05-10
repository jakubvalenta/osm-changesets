from django import forms


class UserForm(forms.Form):
    uid = forms.IntegerField(label="User id")
    user_name = forms.CharField(label="User name")
