from django import forms
from django.test import TestCase
from hittalaget.users.forms import CreateUserForm, UpdateUserForm
from hittalaget.users.models import City, User


class CreateUserFormTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.city = City.objects.create(name="Stockholm")
    cls.user = User.objects.create_user(username="anon", email="anon@test.com", birthday="2000-1-1", city=cls.city)
    cls.form = CreateUserForm()
  
  def test_form_fields(self):
    self.assertEqual(len(self.form.fields), 8)
    self.assertIn("username", self.form.fields)
    self.assertIn("first_name", self.form.fields)
    self.assertIn("last_name", self.form.fields)
    self.assertIn("email", self.form.fields)
    self.assertIn("birthday", self.form.fields)
    self.assertIn("city", self.form.fields)
    self.assertIn("password1", self.form.fields)
    self.assertIn("password2", self.form.fields)

  def test_widgets(self):
    birthday_widget = self.form.fields['birthday'].widget
    self.assertTrue(isinstance(birthday_widget, forms.widgets.SelectDateWidget))
  
  def test_form_labels(self):
    self.assertEqual(self.form.fields['username'].label, "användarnamn:")
    self.assertEqual(self.form.fields['first_name'].label, "förnamn:")
    self.assertEqual(self.form.fields['last_name'].label, "efternamn:")
    self.assertEqual(self.form.fields['email'].label, "email:")
    self.assertEqual(self.form.fields['birthday'].label, "född:")
    self.assertEqual(self.form.fields['city'].label, "stad:")

  def test_unique_error_messages(self):
    form_data = {
      "username": "anon",
      "email": "anon@test.com",
      "birthday": "2000-1-1",
      "city": str(self.city.id),
    }
    form = CreateUserForm(data=form_data)
    form.is_valid()
    self.assertIn("Användarnamnet existerar redan! Prova ett annat och försök igen.", form.errors['username'])
    self.assertIn("Emailadressen existerar redan! Prova en annan och försök igen.", form.errors['email'])
  
  def test_invalid_error_messages(self):
    form_data = {
      "username": "anon",
      "email": "anon @test.com",
      "birthday": "2000-1-1",
      "city": str(self.city.id),
    }
    form = CreateUserForm(data=form_data)
    form.is_valid()
    self.assertIn("Ange en riktig email.", form.errors['email'])


class UpdateUserFormTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.city = City.objects.create(name="Stockholm")
    cls.user = User.objects.create_user(username="anon", email="anon@test.com", birthday="2000-1-1", city=cls.city)
    cls.user2 = User.objects.create_user(username="anon2", email="anon2@test.com", birthday="2000-1-1", city=cls.city)
    cls.form = CreateUserForm()

  def test_form_fields(self):
    self.assertTrue(len(self.form.fields), 5)
    self.assertIn("first_name", self.form.fields)
    self.assertIn("last_name", self.form.fields)
    self.assertIn("email", self.form.fields)
    self.assertIn("birthday", self.form.fields)
    self.assertIn("city", self.form.fields)
  
  def test_widgets(self):
    birthday_widget = self.form.fields['birthday'].widget
    self.assertTrue(isinstance(birthday_widget, forms.widgets.SelectDateWidget))
  
  def test_form_labels(self):
    self.assertEqual(self.form.fields['first_name'].label, "förnamn:")
    self.assertEqual(self.form.fields['last_name'].label, "efternamn:")
    self.assertEqual(self.form.fields['email'].label, "email:")
    self.assertEqual(self.form.fields['birthday'].label, "född:")
    self.assertEqual(self.form.fields['city'].label, "stad:")
  
  def test_unique_error_messages(self):
    form_data = {
      "first_name": "anon",
      "last_name": "nym",
      "email": "anon2@test.com",
      "birthday": "2000-1-1",
      "city": str(self.city.id),
    }
    form = UpdateUserForm(instance=self.user, data=form_data)
    form.is_valid()
    self.assertIn("Emailadressen existerar redan! Prova en annan och försök igen.", form.errors['email'])
  
  def test_invalid_error_messages(self):
    form_data = {
      "first_name": "anon",
      "last_name": "nym",
      "email": "anon @test.com",
      "birthday": "2000-1-1",
      "city": str(self.city.id),
    }
    form = UpdateUserForm(instance=self.user, data=form_data)
    form.is_valid()
    self.assertIn("Ange en riktig email.", form.errors['email'])








  




