from django import forms
from django.core.exceptions import ValidationError
from .models import FootballPlayer, FootballHistory

import datetime


class HistoryMixin: 
    fields = ["start_year", "end_year", "team_name"]

    current_year = datetime.datetime.now().year + 1
    year_range = [(str(year), year) for year in range(1980, current_year)[::-1]]

    widgets = {
        "start_year": forms.Select(choices=year_range),
        "end_year": forms.Select(choices=year_range),
    }

    labels = {
        "start_year": "startdatum:",
        "end_year": "slutdatum:",
        "team_name": "lagnamn:",
    }

    error_messages = {
        "start_year": {
            "required": "Du måste fylla i detta fält.",
            "invalid": "Du måste ange en siffra.",
        },
        "end_year": {
            "required": "Du måste fylla i detta fält.",
            "invalid": "Du måste ange en siffra.",
        },
        "team_name": {
            "required": "Du måste fylla i detta fält.",
        },
    }


class FootballPlayerForm(forms.ModelForm):
    class Meta:
        model = FootballPlayer
        fields = ["positions", "foot", "experience", "special_ability"]

        labels = {
            "positions": "Jag kan spela:",
            "foot": "Min bästa fot:",
            "experience": "Min bästa erfarenhet:",
            "special_ability": "Spetsegenskap:",
        }

        required_msg = "Du måste fylla i detta fält."
        invalid_choice_msg = "Du har valt ett ogiltigt alternativ."

        error_messages = {
            "positions": { 
                "required": required_msg,
                "invalid_choice": invalid_choice_msg,
                "invalid_list": invalid_choice_msg,
                },
            "foot": {
                "required": required_msg,
                "invalid_choice": invalid_choice_msg,
            },
            "experience": {
                "required": required_msg,
                "invalid_choice": invalid_choice_msg,
            },
            "special_ability": {
                "required": required_msg,
                "invalid_choice": invalid_choice_msg,
            },
        }


class FootballHistoryForm(forms.ModelForm):
    class Meta(HistoryMixin):
        model = FootballHistory
    
    current_year = datetime.datetime.now().year

    def clean_start_year(self):
        start_year = self.cleaned_data['start_year']
        if not len(str(start_year)) == 4:
            raise ValidationError("Startåret måste ha det följande formatet: YYYY")
        if start_year > self.current_year:
            raise ValidationError("Startåret kan inte ligga i framtiden.")
        return start_year
    
    def clean_end_year(self):
        end_year = self.cleaned_data['end_year']
        if not len(str(end_year)) == 4:
            raise ValidationError("Slutåret måste ha det följande formatet: YYYY")
        if end_year > self.current_year:
            raise ValidationError("Slutåret kan inte ligga i framtiden.")
        return end_year


    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get("start_year")
        end_year = cleaned_data.get("end_year")

        if start_year and end_year:
            if start_year > end_year:
                self.add_error(
                    'start_year',
                    ValidationError("Startåret kan inte vara senare än slutåret.")
                )
        return cleaned_data
        

