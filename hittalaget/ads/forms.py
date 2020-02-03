from django import forms
from django.core.exceptions import ValidationError
from django.http import Http404
from .models import Ad
from .form_choices import (
    football_positions,
    football_min_experience,
    football_special_ability,
)

import datetime


class AdForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport')
        super().__init__(*args, **kwargs)

        positions = {
            "fotboll": football_positions,
        }
        min_experience = {
            "fotboll": football_min_experience,
        }
        special_ability = {
            "fotboll": football_special_ability,
        }

        try:
            self.fields['positions'].widget = forms.Select(choices=positions[sport])
            self.fields['min_experience'].widget = forms.Select(choices=min_experience[sport])
            self.fields['special_ability'].widget = forms.Select(choices=special_ability[sport])
        except KeyError:
            raise Http404()

    
    class Meta:
        model = Ad
        fields = [
            'description',
            'positions',
            'min_experience',
            'special_ability',
        ]

        labels = {
            "description": "Kort beskrivning av vad du söker:",
            "positions": "Vilken position ska spelaren ha?",
            "min_experience": "Vad är den lägsta erfarenhet spelaren ska ha?",
            "special_ability": "Vilken spetsegenskap ska spelaren ha?",
        }
        
        error_messages = {
            "description": {
                "required": "",
            },
            "positions": {
                "required": "",
            },
            "min_experience": {
                "required": "",
            },
            "special_ability": {
                "required": "",
            },
        }


'''
AdForm

- dynamic add experience, position, and special ability field
- do I need cleaning? (only if you need custom validation that is not caught naturally — don’t have to make any check to see whether title exist already, etc.. so it’s fine..) — or if you need to alter value before it hits the database.. if you always want to do that, you better use a signal instead.. then it will happen no matter if you are using a form or not..
- perhaps custom validation => raise validation if you choose a sport you don’t have a team for.. because you will be able to pick a sport…

// save positions, and experience in it’s own file that you import..
'''