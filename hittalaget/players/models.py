from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from multiselectfield import MultiSelectField
import datetime


class FootballPlayer(models.Model):

    class Position(models.TextChoices):
        MÅLVAKT = "målvakt"
        FÖRSVARARE = "försvarare"
        VÄNSTERBACK = "vänsterback"
        HÖGERBACK = "högerback"
        MITTBACK = "mittback"
        MITTFÄLTARE = "mittfältare"
        VÄNSTERMITTFÄLTARE = "vänstermittfältare"
        HÖGERMITTFÄLTARE = "högermittfältare"
        CENTRALMITTFÄLTARE = "centralmittfältare"
        ANFALLARE = "anfallare"
    
    class Foot(models.TextChoices):
        HÖGER = "höger"
        VÄNSTER = "vänster"
        DUBBELFOTAD = "dubbelfotad"
    
    class Experience(models.TextChoices):
        UNGDOMSFOTBOLL = "ungdomsfotboll"
        KORPEN = "korpen"
        DIVISION_8 = "division 8"
        DIVISION_7 = "division 7"
        DIVISION_6 = "division 6"
        DIVISION_5 = "division 5"
        DIVISION_4 = "division 4"
        DIVISION_3 = "division 3"
        DIVISION_2 = "division 2"
        DIVISION_1 = "division 1"
        SUPERETTAN = "superettan"
        ALLSVENSKAN = "allsvenskan"

    class SpecialAbility(models.TextChoices):
        SNABB = "snabb"
        UTHÅLLIG = "uthållig"
        ALLROUND = "allround"
        POSITIONERING = "positionering"
        HUVUDSPEL = "huvudspel"
        LEDARGESTALT = "ledargestalt"
        SNABBA_REFLEXER = "snabba reflexer"
        SKOTT = "skott"
        SPELFÖRSTÅELSE = "spelförståelse"
        INLÄGG = "inlägg"
        LÅNGBOLLAR = "långbollar"
        FRISPARKAR = "frisparkar"
        DRIBBLA = "dribbla"
        TACKlA = "tackla"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="football_player"
    )
    sport = models.CharField(max_length=50, default="fotboll")
    username = models.CharField(max_length=50, unique=True)
    positions = MultiSelectField(max_length=255, choices=Position.choices)
    foot = models.CharField(max_length=255, choices=Foot.choices)
    experience = models.CharField(max_length=255, choices=Experience.choices)
    special_ability = models.CharField(max_length=255, choices=SpecialAbility.choices)
    is_available = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to="images/players/football/", 
        default="images/players/football/default_football_player.jpg",
        blank=True, 
        null=True
    )

    def get_absolute_url(self):
        return reverse("player:detail", kwargs={"sport": "fotboll", "username": self.username })
    

class History(models.Model):
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField()
    team_name = models.CharField(max_length=25)

    class Meta:
        abstract = True

                
class FootballHistory(History):
    ''' Each instance is a history entry attached to a particular football player. '''
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE, related_name="history_entries")    
    
