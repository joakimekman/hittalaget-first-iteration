from django.db import models
from django.db.models.signals import pre_save 
from django.conf import settings
from hittalaget.ads.models import Ad
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField



#   ---------------------------------------   #
#   ~~~~~~~~~~   CONVERSATIONS   ~~~~~~~~~~   #            
#   ---------------------------------------   #


class Conversation(models.Model):
    ''' Abastract base class. '''
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    users_arr = ArrayField(models.CharField(max_length=255))

    class Meta:
        abstract = True


class PmConversation(Conversation):
    tag = models.CharField(max_length=255, default="pm")


class AdConversation(Conversation):
    tag = models.CharField(max_length=255, default="ad")
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    conversation_id = models.IntegerField(unique=True) # add it as an index later for faster lookups
    is_active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("conversation:ad_detail", kwargs={"conversation_id": self.conversation_id})


def pre_save_conversation_id(sender, instance, **kwargs):
    from random import randint
    rand_id = randint(100000, 999999)
    
    if not instance.conversation_id: 
        while AdConversation.objects.filter(conversation_id=rand_id).exists():
            rand_id = randint(100000, 999999)
        else:
            instance.conversation_id = rand_id
    
pre_save.connect(pre_save_conversation_id, sender=AdConversation)


#   ---------------------------------------   #
#   ~~~~~~~~~~~~~   MESSAGES   ~~~~~~~~~~~~   #            
#   ---------------------------------------   #


class Message(models.Model):
    ''' Abstract base class. '''
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        abstract = True


class PmMessage(Message):
    ''' Messages added to a PmConversation. '''
    conversation = models.ForeignKey(PmConversation, on_delete=models.CASCADE, related_name="messages")


class AdMessage(Message):
    ''' Messages added to an AdConversation. '''
    conversation = models.ForeignKey(AdConversation, on_delete=models.CASCADE, related_name="messages")




    





