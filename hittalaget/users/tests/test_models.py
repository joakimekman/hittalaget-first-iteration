from django.test import TestCase
from django.urls import reverse
from hittalaget.users.models import City, User
from hittalaget.users.forms import CreateUserForm


class CityModelTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.city = City.objects.create(name="Stockholm")
  
  def test_str_representation(self):
    self.assertTrue(self.city, "Stockholm")


class UserModelTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.city = City.objects.create(name="Stockholm")
    cls.user = User.objects.create_user(username="anon", email="test@test.com", birthday="2000-1-1", city=cls.city)

  def test_get_absolute_url(self):
    expected_url = reverse("user:detail", kwargs={"username": self.user})
    self.assertTrue(self.user.get_absolute_url, expected_url)

  def test_str_representation(self):
    self.assertTrue(self.user, "anon")

  def test_clean(self): 
    form_data = {
      "username": "TeSt",
      "first_name": "Test",
      "last_name": "Ing",
      "email": "Test@AnoN.com",
      "birthday": "2000-1-1",
      "city": str(self.city.id),
      "password1": "test",
      "password2": "test",
    }
    form = CreateUserForm(data=form_data)
    if form.is_valid():
      form.save()
    else:
      print(form.errors)
      
    last_user = User.objects.last()
    self.assertEqual(last_user.username, "test")
    self.assertEqual(last_user.email, "test@anon.com")


    
    

