from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class City(models.Model):
  name = models.CharField(max_length=50, unique=True)

  def __str__(self):
    return self.name


class User(AbstractUser):
  username = models.CharField(max_length=30, unique=True)
  first_name = models.CharField(max_length=30, verbose_name='first name')
  last_name = models.CharField(max_length=150, verbose_name='last name')
  email = models.EmailField(unique=True, verbose_name='email address')
  birthday = models.DateTimeField()
  height = models.FloatField(blank=True, null=True)
  city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="users")

  def get_absolute_url(self):
    return reverse("user:detail", kwargs={ "username": self.username })

  def __str__(self):
    return self.username
  
  def clean(self):
    """ Called by form.is_valid() """
    self.username = self.username.lower()
    self.email = self.email.lower()



