from django.contrib.auth import get_user_model
from django import forms
from django.test import TestCase
from hittalaget.players.forms import FootballPlayerForm, FootballHistoryForm
from hittalaget.users.models import City, User
import datetime

User = get_user_model()


class FootballPlayerFormTest(TestCase):
    
    def test_fields(self):
        form = FootballPlayerForm()
        self.assertEqual(len(form.fields), 4)
        self.assertIn("positions", form.fields)
        self.assertIn("foot", form.fields)
        self.assertIn("experience", form.fields)
        self.assertIn("special_ability", form.fields)
    
    def test_labels(self):
        form = FootballPlayerForm()
        self.assertEqual(form.fields['positions'].label, "Jag kan spela:")
        self.assertEqual(form.fields['foot'].label, "Min bästa fot:")
        self.assertEqual(form.fields['experience'].label, "Min bästa erfarenhet:")
        self.assertEqual(form.fields['special_ability'].label, "Spetsegenskap:")
    
    def test_blank_data(self):
        form = FootballPlayerForm(data={})        
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)
        self.assertIn("Du måste fylla i detta fält.", form.errors['positions'])
        self.assertIn("Du måste fylla i detta fält.", form.errors['foot'])
        self.assertIn("Du måste fylla i detta fält.", form.errors['experience'])
        self.assertIn("Du måste fylla i detta fält.", form.errors['special_ability'])
    
    def test_invalid_data(self):
        form_data = {
            "positions": "anfallare",
            "foot": "x",
            "experience": "x",
            "special_ability": "x",
        }
        form = FootballPlayerForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)
        self.assertIn("Du har valt ett ogiltigt alternativ.", form.errors['positions'])
        self.assertIn("Du har valt ett ogiltigt alternativ.", form.errors['foot'])
        self.assertIn("Du har valt ett ogiltigt alternativ.", form.errors['experience'])
        self.assertIn("Du har valt ett ogiltigt alternativ.", form.errors['special_ability'])

    def test_valid_data(self):
        form_data = {
            "positions": ["anfallare", "målvakt"],
            "foot": "höger",
            "experience": "korpen",
            "special_ability": "snabb",
        }
        form = FootballPlayerForm(data=form_data)
        self.assertTrue(form.is_valid())
    

class HistoryFormTest(TestCase):
    
    def test_fields(self):
        form = FootballHistoryForm()
        self.assertEqual(len(form.fields), 3)
        self.assertIn("start_year", form.fields)
        self.assertIn("end_year", form.fields)
        self.assertIn("team_name", form.fields)
    
    def test_widgets(self):
        form = FootballHistoryForm()
        self.assertIsInstance(form.fields['start_year'].widget, forms.Select)
        self.assertIsInstance(form.fields['end_year'].widget, forms.Select)

    def test_labels(self):
        form = FootballHistoryForm()
        self.assertEqual(form.fields['start_year'].label, "startdatum:")
        self.assertEqual(form.fields['end_year'].label, "slutdatum:")
        self.assertEqual(form.fields['team_name'].label, "lagnamn:")

    def test_blank_data(self):
        form = FootballHistoryForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        self.assertIn("Du måste fylla i detta fält.", form.errors['start_year'])
        self.assertIn("Du måste fylla i detta fält.", form.errors['end_year'])
        self.assertIn("Du måste fylla i detta fält.", form.errors['team_name'])

    def test_invalid_data(self):
        form_data = {
            "start_year": True,
            "end_year": True,
            "team_name": "Örebro SK",
        }
        form = FootballHistoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertIn("Du måste ange en siffra.", form.errors['start_year'])
        self.assertIn("Du måste ange en siffra.", form.errors['end_year'])

    def test_valid_data(self):
        form_data = {
            "start_year": "2000",
            "end_year": "2001",
            "team_name": "Örebro SK",
        }
        form = FootballHistoryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_year_format(self):
        form_data = {
            "start_year": "200",
            "end_year": "201",
            "team_name": "Örebro SK",
        }
        form = FootballHistoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Startåret måste ha det följande formatet: YYYY", form.errors['start_year'])
        self.assertIn("Slutåret måste ha det följande formatet: YYYY", form.errors['end_year'])
    
    def test_clean_future_year(self):
        current_year = datetime.datetime.now().year
        form_data = {
            "start_year": current_year + 1,
            "end_year": current_year + 2,
            "team_name": "Örebro SK",
        }
        form = FootballHistoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Startåret kan inte ligga i framtiden.", form.errors['start_year'])
        self.assertIn("Slutåret kan inte ligga i framtiden.", form.errors['end_year'])

    
    def test_clean_start_and_end_year(self):
        ''' Making sure start year is not greater than the end year. '''
        form_data = {
            "start_year": "2010",
            "end_year": "2005",
            "team_name": "Örebro SK",
        }
        form = FootballHistoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Startåret kan inte vara senare än slutåret.", form.errors['start_year'])






    
        
    






