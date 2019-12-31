from django import forms as django_forms
from django.contrib.auth import forms, get_user_model
from django.core.exceptions import ValidationError
import datetime

User = get_user_model()


class MetaMixin:
    current_year = datetime.datetime.now().year

    MONTHS = {
        1: "januari",
        2: "februari",
        3: "mars",
        4: "april",
        5: "maj",
        6: "juni",
        7: "juli",
        8: "augusti",
        9: "september",
        10: "oktober",
        11: "november",
        12: "december",
    }

    widgets = {
        "birthday": django_forms.SelectDateWidget(
            years=range(current_year, current_year - 80, -1), months=MONTHS
        ),
    }


class CreateUserForm(forms.UserCreationForm):
    class Meta(MetaMixin, forms.UserCreationForm.Meta):
        model = User
        fields = forms.UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "email",
            "birthday",
            "city",
        )

        labels = {
            "username": "användarnamn:",
            "first_name": "förnamn:",
            "last_name": "efternamn:",
            "email": "email:",
            "birthday": "född:",
            "city": "stad:",
        }

        error_messages = {
            "username": {
                "unique": "Användarnamnet existerar redan! Prova ett annat och försök igen.",
            },
            "email": {
                "unique": "Emailadressen existerar redan! Prova en annan och försök igen.",
                "invalid": "Ange en riktig email.",
            },
        }


class UpdateUserForm(django_forms.ModelForm):
    class Meta(MetaMixin):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "birthday",
            "city"
        ]

        labels = {
            "first_name": "förnamn:",
            "last_name": "efternamn:",
            "email": "email:",
            "birthday": "född:",
            "city": "stad:",
        }

        error_messages = {
            "email": {
                "unique": "Emailadressen existerar redan! Prova en annan och försök igen.",
                "invalid": "Ange en riktig email.",
            },
        }

