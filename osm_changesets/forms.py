from django import forms
from django.core.exceptions import ValidationError


class ChangesetQueryForm(forms.Form):
    uid = forms.IntegerField(
        label="Enter user id",
        widget=forms.TextInput(attrs={"placeholder": "4151758"}),
        required=False,
    )
    display_name = forms.CharField(
        label="or display name",
        widget=forms.TextInput(attrs={"placeholder": "Jakub Valenta"}),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        uid = cleaned_data.get("uid")
        display_name = cleaned_data.get("display_name")
        if not uid and not display_name:
            raise ValidationError("Enter a user id or display name.")
        if uid and display_name:
            raise ValidationError("Enter only one of user id or display name.")
