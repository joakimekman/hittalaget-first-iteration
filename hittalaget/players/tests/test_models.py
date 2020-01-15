from django.test import TestCase
from django.urls import reverse
from hittalaget.players.models import FootballPlayer, FootballHistory
from hittalaget.players.forms import FootballHistoryForm
from django.contrib.auth import get_user_model
from hittalaget.users.models import City
from hittalaget.players.forms import FootballPlayerForm, FootballHistoryForm

import datetime

User = get_user_model()


class FootballPlayerTest(TestCase):
    """ Testing the model FootballPlayer. """
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(name="Stockholm")
        cls.user = User.objects.create_user(
            username="anon",
            first_name="anon",
            last_name="nym",
            email="anon@nym.com",
            birthday="2000-1-1",
            city=cls.city
        )
        cls.football_player = FootballPlayer.objects.create(
            user=cls.user,
            username=cls.user.username,
            positions="['målvakt', 'anfallare]",
            foot="höger",
            experience="korpen",
            special_ability="snabb"
        )

    def test_get_absolute_url(self):
        expected_url = reverse("player:detail", kwargs={
            "sport": self.football_player.sport,
            "username": self.football_player.username,
        })
        self.assertTrue(self.football_player.get_absolute_url, expected_url)




    
    

