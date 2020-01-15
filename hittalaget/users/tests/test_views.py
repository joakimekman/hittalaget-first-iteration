from django.test import TestCase, Client
from django.urls import reverse
from hittalaget.users.models import City, User


class CreateViewTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.client = Client()
    cls.city = City.objects.create(name="Stockholm")
    cls.user = User.objects.create_user(
      username="anon",
      email="anon@test.com",
      birthday="2000-1-1",
      city=cls.city
    )
    cls.url = reverse('user:register')

  def test_unauthorized_GET(self):
    """ Ensures a 200 is returned and that the right template is rendered
    when requesting to view the create page while unauthorized. """
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'registration/register.html')

  def test_authorized_GET(self):
    """ Ensures a 302 is returned and that a user gets redirected to his/her
    detail page when requesting to view the create page while authorized. """
    self.client.force_login(self.user)
    response = self.client.get(self.url)
    self.assertRedirects(
      response, 
      reverse('user:detail', kwargs={"username": self.user.username}),
      status_code=302,
      target_status_code=200
    )

  def test_POST_and_success_url(self):
    """ Ensures that a user can be created and automatically logged in. """
    response = self.client.post(self.url, {
      'username': 'test',
      'first_name': 'anon',
      'last_name': 'nymous',
      'email': 'test@test.com',
      'birthday': '2000-1-1',
      'city': str(self.city.id),
      'password1': 'pw',
      'password2': 'pw',
    }, follow=True)
    self.assertTrue(User.objects.filter(username="test").exists())
    self.assertRedirects(
      response, 
      reverse('user:detail', kwargs={"username": "test"}),
      status_code=302,
      target_status_code=200
    )
    self.assertEqual(response.wsgi_request.user.username, "test")
    # get message from context and check that expected text is there
    message = list(response.context.get('messages'))[0]
    self.assertEqual(message.tags, "success")
    self.assertTrue("Ditt konto har skapats!" in message.message)
  

class DetailViewTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.client = Client()
    cls.city = City.objects.create(name="Stockholm")
    cls.user = User.objects.create_user(
      username="anon",
      birthday="2000-1-1",
      city=cls.city
    )
    cls.url = reverse('user:detail', kwargs={"username": cls.user})

  def test_GET_active_user(self):
    """ Ensures a 200 is returned and that the right template is rendered
    when requesting to view the detail page of an active user. """
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'users/detail.html')

  def test_GET_inactive_user(self):
    """ Ensures a 404 is raised when requesting to view the detail page
    of an inactive user. """
    inactive_user = User.objects.create_user(
      username="anon2",
      email="anon2@test.com",
      birthday="2000-1-1",
      city=self.city, 
      is_active=False,
    )
    response = self.client.get(reverse('user:detail', kwargs={"username": inactive_user}))
    self.assertEqual(response.status_code, 404)  

  def test_GET_invalid_user(self):
    """ Ensures a 404 is raised when requesting to view the detail page
    of an invalid user. """
    response = self.client.get(reverse('user:detail', kwargs={"username": "sdf"}))
    self.assertEqual(response.status_code, 404)

  def test_get_object(self):
    """ Ensure object is the user specified in the URL params. """
    response = self.client.get(self.url)
    self.assertEqual(response.context['object'], self.user)


class LoginViewTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.client = Client()
    cls.city = City.objects.create(name="Stockholm")
    cls.user = User.objects.create_user(username="anon", email="anon@test.com", birthday="2000-1-1", city=cls.city)
    cls.url = reverse('user:login')

  def test_unauthorized_GET(self):
    """ Ensures a 200 is returned and that the right template is rendered
    when requesting to view the login page while unauthorized. """
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'registration/login.html')

  def test_authorized_GET(self):
    """ Ensures a 302 redirect to detail page is performed when requesting
    to view the login page while authorized. """
    self.client.force_login(self.user)
    response = self.client.get(self.url)
    self.assertRedirects(
      response, 
      reverse('user:detail', kwargs={"username": self.user}),
      status_code=302,
      target_status_code=200
    )


class RedirectViewTest(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.client = Client()
    cls.city = City.objects.create(name="Stockholm")
    cls.user = User.objects.create_user(username="anon", email="anon@test.com", birthday="2000-1-1", city=cls.city)
    cls.url = reverse('user:redirect')

  def test_authorized_GET(self):
    """ Ensures a 302 redirect to detail page is performed if authorized. """
    self.client.force_login(self.user)
    response = self.client.get(self.url)
    self.assertRedirects(
      response, 
      reverse('user:detail', kwargs={"username": self.user}),
      status_code=302,
      target_status_code=200
    )

  def test_unauthorized_GET(self):
    """ Ensures a 302 redirect to login page is performed if unauthorized. """
    response = self.client.get(self.url)
    self.assertRedirects(
      response, 
      '/logga-in/?next=/~redirect/', 
      status_code=302, 
      target_status_code=200
    )


class UpdateViewTest(TestCase):

  def setUp(self):
    self.client = Client()
    self.city = City.objects.create(name="Stockholm")
    self.user = User.objects.create_user(username="anon", email="anon@test.com", birthday="2000-1-1", city=self.city)
    self.url = reverse('user:update_account')

  def test_unauthorized_GET(self):
    """ Ensures a 302 redirect to the login page is performed if unauthorized user try
    to access the update page. """
    response = self.client.get(self.url)
    self.assertRedirects(
      response, 
      '/logga-in/?next=/installningar/',
      status_code=302,
      target_status_code=200
    )

  def test_authorized_GET(self):
    """ Ensures a 200 is returned and that the right template is rendered 
    if an authorized user request to view the update page. """
    self.client.force_login(self.user)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'users/update.html')

  def test_get_object(self):
    """ Ensures object is the user specified in the URL. """
    self.client.force_login(self.user)
    response = self.client.get(self.url)
    self.assertEqual(response.context['object'], self.user)

  def test_POST_and_success_url(self):
    """ Ensures a 302 redirect to the detail page is performed if user is
    successfully updated with valid POST data. """
    self.client.force_login(self.user)
    response = self.client.post(self.url, {
      "first_name": "test",
      "last_name": "nymous",
      "email": "anon@test.com",
      "birthday": "2000-1-1",
      "city": str(self.city.id),
    }, follow=True)
    self.user.refresh_from_db()
    self.assertRedirects(
      response, 
      reverse('user:detail', kwargs={"username": self.user}),
      status_code=302,
      target_status_code=200
    )
    self.assertEqual(self.user.first_name, 'test')
    # get message from context and check that expected text is there
    message = list(response.context.get('messages'))[0]
    self.assertEqual(message.tags, "success")
    self.assertTrue("Inställningarna sparades!" in message.message)


class DeleteViewTest(TestCase):

  def setUp(self):
    self.client = Client()
    self.city = City.objects.create(name="Stockholm")
    self.user = User.objects.create_user(username="anon", email="anon@test.com", birthday="2000-1-1", city=self.city)
    self.url = reverse('user:delete_account')

  def test_unauthorized_GET(self):
    """ Ensures a 302 redirect to the login page is performed if unauthorized user try
    to delete its user account. """
    response = self.client.get(self.url)
    self.assertRedirects(
      response,
      '/logga-in/?next=/ta-bort-konto/',
      status_code=302,
      target_status_code=200
    )
  
  def test_authorized_GET(self):
    """ Ensures a 200 is returned and the confirm page is rendered if an
    authorized user request to delete its user account. """
    self.client.force_login(self.user)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'users/user_confirm_delete.html')
    
  def test_delete_user_and_success_url(self):
    """ Ensures a 302 redirect to index page is performed if an authorized user
    succssfully "delete" its user account. """
    self.client.force_login(self.user)
    response = self.client.post(self.url)
    self.assertRedirects(
      response,
      reverse('index'),
      status_code=302,
      target_status_code=200
    )
    self.user.refresh_from_db()
    self.assertFalse(self.user.is_active)
    self.assertNotEqual(response.wsgi_request.user, self.user)
  

class PasswordChangeViewTest(TestCase):

  def setUp(self):
    self.client = Client()
    self.city = City.objects.create(name="Stockholm")
    self.user = User.objects.create_user(
      username="anon",
      email="anon@test.com",
      birthday="2000-1-1",
      city=self.city,
      password="pw"
    )
    self.url = reverse('user:password_change')

  def test_unauthorized_GET(self):
    """ Ensures a 302 redirect to the login page is performed if unauthorized user try
    to access the password change page. """
    response = self.client.get(self.url)
    self.assertRedirects(
      response,
      '/logga-in/?next=/byt-losenord/',
      status_code=302,
      target_status_code=200
    )

  def test_authorized_GET(self):
    """ Ensures a 200 is returned and that the right template is rendered
    if an authorized user request to view the password change page. """
    self.client.force_login(self.user)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)

  def test_POST_and_success_url(self):
    """ Ensures a 302 redirect to the detail page is performed if password is
    successfully updated with valid POST data. """
    self.client.force_login(self.user)
    data = {
      'old_password': 'pw',
      'new_password1': 'newpw',
      'new_password2': 'newpw',
    }
    response = self.client.post(reverse('user:password_change'), data, follow=True)
    self.user.refresh_from_db()
    self.assertTrue(self.user.check_password('newpw'))
    self.assertRedirects(
      response,
      reverse('user:detail', kwargs={"username": self.user}),
      status_code=302,
      target_status_code=200
    )
    # get message from context and check that expected text is there
    message = list(response.context.get('messages'))[0]
    self.assertEqual(message.tags, "success")
    self.assertTrue("Ditt lösenord har ändrats!" in message.message)