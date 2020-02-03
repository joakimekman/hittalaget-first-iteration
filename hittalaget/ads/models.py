from django.db import models
from django.db.models.signals import pre_save 
from hittalaget.teams.models import Team
from django.utils.text import slugify
from django.urls import reverse

## must add age to the list.. and of course height..


class Ad(models.Model):

    class Sport(models.TextChoices):
        FOTBOLL = "fotboll"

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    title = models.CharField(max_length=255) # blank? if you save it anyway.. in any form/model/signal function, it's fine?
    description = models.TextField(max_length=500)
    positions = models.CharField(max_length=255)
    min_experience = models.CharField(max_length=255)
    special_ability = models.CharField(max_length=255)
    sport = models.CharField(max_length=255, choices=Sport.choices)
    slug = models.SlugField()
    ad_id = models.IntegerField(unique=True)

    def get_absolute_url(self):
        return reverse("ad:detail", kwargs={"sport": self.sport, "ad_id": self.ad_id, "slug": self.slug})


def pre_save_title(sender, instance, **kwargs):
    instance.title = "{} söker {}".format(
        instance.team,
        instance.positions
    )
    
def pre_save_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.title)

def pre_save_ad_id(sender, instance, **kwargs):
    from random import randint
    rand_id = randint(100000, 999999)
    
    if not instance.ad_id: 
        while Ad.objects.filter(ad_id=rand_id).exists():
            rand_id = randint(100000, 999999)
        else:
            instance.ad_id = rand_id
    
pre_save.connect(pre_save_title, sender=Ad)
pre_save.connect(pre_save_slug, sender=Ad)
pre_save.connect(pre_save_ad_id, sender=Ad)