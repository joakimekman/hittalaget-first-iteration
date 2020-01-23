from django import forms
from django.core.exceptions import ValidationError
from .models import Team
from .levels import football_levels
from django.http import HttpResponseRedirect, Http404, HttpResponse
import datetime


class TeamForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.sport = kwargs.pop("sport")
        super().__init__(*args, **kwargs)

        ''' Generate choices based on the sport passed from the view. '''
        ''' make sure there are no key error '''

        level = {
            "fotboll": football_levels,
        }        
        
        try:
            self.fields['level'].widget = forms.Select(choices=level[self.sport])
        except KeyError:
            raise Http404()

    class Meta:
        model = Team
        fields = ['founded', 'home', 'city', 'website', 'level']

        current_year = datetime.datetime.now().year + 1
        year_range = [(str(year), year) for year in range(1880, current_year)[::-1]]

        widgets = {
            "founded": forms.Select(choices=year_range),
        }

        labels = {
            'founded': 'Grundades:',
            'home': 'Hemmaplan:',
            'city': 'Stad:',
            'website': 'Hemsida:',
            'level': 'Liga:',
        }

        help_texts = {
            'website': "http://example.com"
        }

        required_msg = "Du måste fylla i detta fält."

        error_messages = {
            'founded': {
                'required': required_msg,
            },
            'home': {
                'required': required_msg,
            },
            'city': {
                'required': required_msg,
            },
            'homepage': {
                'required': required_msg,
            },
            'level': {
                'required': required_msg,
            },
        }


class TeamCreateForm(TeamForm):
    class Meta(TeamForm.Meta):
        ''' Include support for a sport and name field. '''
        fields = TeamForm.Meta.fields + ['sport', 'name']

        TeamForm.Meta.labels.update({
            'sport': 'Sport:',
            'name': 'Namn:',
        })
        
        TeamForm.Meta.error_messages.update({
            'sport': {
                'required': TeamForm.Meta.required_msg,
            },
            'name': {
                'required': TeamForm.Meta.required_msg,
            },
        })
