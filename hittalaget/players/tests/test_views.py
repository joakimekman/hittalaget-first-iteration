from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from hittalaget.players.models import FootballPlayer, FootballHistory
from hittalaget.players.forms import FootballPlayerForm, FootballHistoryForm
from hittalaget.users.models import City

User = get_user_model()


#   ---------------------------------------   #
#   ~~~~~~~~~~~~~~   MIXINS   ~~~~~~~~~~~~~   #            
#   ---------------------------------------   #


class SetUpTestDataMixin:
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(name="Stockholm")

        # user with a football profile
        cls.user = User.objects.create_user(
            username="anon",
            email="anon@test.com",
            birthday="2000-1-1",
            city=cls.city
        )

        # user without a football profile
        cls.user2 = User.objects.create_user(
            username="anon2",
            email="anon2@test2.com",
            birthday="2000-1-1",
            city=cls.city
        )

        FootballPlayer.objects.create(
            user=cls.user,
            username=cls.user.username,
            positions="['målvakt', 'anfallare]",
            foot="höger",
            experience="korpen",
            special_ability="snabb"
        )
        
        cls.form_data = {
            "positions": "anfallare",
            "foot": "höger",
            "experience": "korpen",
            "special_ability": "snabb",
        }


class SetUpMixin:
    def setUp(self):
        self.city = City.objects.create(name="Stockholm")
        
        # user with a football profile
        self.user = User.objects.create_user(
            username="anon",
            email="anon@test.com",
            birthday="2000-1-1",
            city=self.city
        )
        
        # user without a football profile
        self.user2 = User.objects.create_user(
            username="anon2",
            email="anon2@test2.com",
            birthday="2000-1-1",
            city=self.city
        )

        FootballPlayer.objects.create(
            user=self.user,
            username=self.user.username,
            positions="['målvakt', 'anfallare]",
            foot="höger",
            experience="korpen",
            special_ability="snabb"
        )

        self.form_data = {
            "positions": "anfallare",
            "foot": "höger",
            "experience": "korpen",
            "special_ability": "snabb",
        }


#   ---------------------------------------   #
#   ~~~~~~~~   TEST PLAYER VIEWS   ~~~~~~~~   #            
#   ---------------------------------------   #


class DetailViewTest(SetUpTestDataMixin, TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("player:detail", kwargs={
            "sport": "fotboll",
            "username": cls.user.username,
        })

    def test_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "players/detail.html")
        self.assertEqual(response.context['object'], self.user.football_player)
        self.assertIn("status", response.context)

    def test_GET_invalid_sport(self):
        url = reverse("player:detail", kwargs={
            "sport": "asd",
            "username": self.user.username,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_GET_invalid_player(self):
        url = reverse("player:detail", kwargs={
            "sport": "football",
            "username": "asd",
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class CreateViewTest(SetUpTestDataMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("player:create", kwargs={"sport": "fotboll"})

    def test_unauthorized_GET(self):
        ''' Since the piece of logic that handle authorization is
        located in the dispatch method, the same test result would
        apply to an unauthorized POST request. '''
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            "/logga-in/?next=/spelare/fotboll/ny/",
            status_code=302,
            target_status_code=200
        )  

    def test_authorized_GET_with_profile(self):
        ''' Since the profile check occurs in the dispatch method,
        the same test result would apply to an authorized POST request
        with a profile. '''
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse("player:detail", kwargs={
                "sport": "fotboll",
                "username": self.user.username,
            }),
            status_code=302,
            target_status_code=200,
        )

    def test_authorized_GET_without_profile(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "players/create.html")
        self.assertIsInstance(response.context['form'], FootballPlayerForm)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, '<ul id="id_positions">')
        self.assertContains(response, '<select name="foot" required id="id_foot">')
        self.assertContains(response, '<select name="experience" required id="id_experience">')
        self.assertContains(response, '<select name="special_ability" required id="id_special_ability">')

    def test_authorized_POST_without_profile(self):
        self.client.force_login(self.user2)
        response = self.client.post(self.url, self.form_data, follow=True)
        self.assertRedirects(
            response,
            reverse("player:detail", kwargs={
                "sport": "fotboll",
                "username": self.user2.username,
            }),
            status_code=302,
            target_status_code=200,
        )
        
        ''' Making sure the player profile is created, and that the user
        and username property is properly assigned. '''
        football_player = FootballPlayer.objects.last()
        self.assertEqual(football_player.user, self.user2)
        self.assertEqual(football_player.username, self.user2.username)
        
        ''' Making sure the right message is returned. '''
        the_message = list(response.context.get('messages'))[0]
        self.assertEqual(the_message.tags, "success")
        self.assertEqual(the_message.message, "Spelarprofilen skapades utan problem!")        

    def test_authorized_POST_invalid_data(self):
        """ If someone tampers with the form field values through inspect. """
        self.client.force_login(self.user2)
        invalid_form_data = {
            "positions": "x",
            "foot": "x",
            "experience": "x",
            "special_ability": "x",
        }
        response = self.client.post(self.url, invalid_form_data)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(len(response.context['form'].errors), 4)
        self.assertContains(
            response,
            '<ul class="errorlist"><li>Du har valt ett ogiltigt alternativ.</li></ul>',
            4
        )

    def test_authorized_POST_blank_data(self):
        self.client.force_login(self.user2)
        response = self.client.post(self.url, {})
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(len(response.context['form'].errors), 4)
        self.assertContains(
            response,
            '<ul class="errorlist"><li>Du måste fylla i detta fält.</li></ul>',
            4
        )

    def test_authorized_GET_invalid_sport(self):
        ''' Since the piece of logic that handle invalid path converters are
        located in the dispatch method, the same test result would apply
        to an authorized POST request with an invalid sport. '''
        url = reverse("player:create", kwargs={"sport": "asd"})
        self.client.force_login(self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class UpdateViewTest(SetUpMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("player:update", kwargs={"sport": "fotboll"})

    def test_unauthorized_GET(self):
        ''' Since the piece of logic that handle authorization is
        located in the dispatch method, the same test result would
        apply to an unauthorized POST request. '''
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            "/logga-in/?next=/spelare/fotboll/uppdatera/",
            status_code=302,
            target_status_code=200
        )

    def test_authorized_GET_with_profile(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "players/update.html")
        self.assertEqual(response.context['object'], self.user.football_player)
        self.assertIsInstance(response.context['form'], FootballPlayerForm)
        # must add more checks => see template

    def test_authorized_POST_with_profile(self):
        self.client.force_login(self.user)
        form_data = {
            "positions": "anfallare",
            "foot": "vänster", # change "höger" to "vänster"
            "experience": "korpen",
            "special_ability": "snabb",
        }
        response = self.client.post(self.url, form_data, follow=True)
        self.user.football_player.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("player:detail", kwargs={
                "sport": "fotboll",
                "username": self.user.username,
            })
        )

        ''' Making sure the foot property was updated. '''
        self.assertEqual(self.user.football_player.foot, "vänster")

        ''' Making sure the right message is returned. '''
        the_message = list(response.context.get('messages'))[0]
        self.assertEqual(the_message.tags, "success")
        self.assertEqual(the_message.message, "Profilen har uppdaterats!")
    
    def test_authorized_GET_without_profile(self):
        ''' Since the profile check occurs in the dispatch method,
        the same test result would apply to an authorized POST request
        with a profile. '''
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse("player:create", kwargs={"sport": "fotboll"}),
            status_code=302,
            target_status_code=200,
        )
    
    def test_authorized_POST_blank_data(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {})
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(len(response.context['form'].errors), 4)
    
    def test_authorized_POST_invalid_data(self):
        self.client.force_login(self.user)
        invalid_form_data = {
            "positions": "x",
            "foot": "x",
            "experience": "x",
            "special_ability": "x",
        }
        response = self.client.post(self.url, invalid_form_data)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(len(response.context['form'].errors), 4)

    def test_authorized_GET_invalid_sport(self):
        ''' Since the piece of logic that handle invalid path converters are
        located in the dispatch method, the same test result would apply
        to an authorized POST request with an invalid sport. '''
        url = reverse("player:create", kwargs={"sport": "asd"})
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DeleteViewTest(SetUpMixin, TestCase):
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("player:delete", kwargs={"sport": "fotboll"})

    def test_unauthorized_GET(self):
        ''' Since the piece of logic that handle authorization is
        located in the dispatch method, the same test result would
        apply to an unauthorized POST request. '''
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            "/logga-in/?next=/spelare/fotboll/ta-bort/",
            status_code=302,
            target_status_code=200,
        )

    def test_authorized_GET_with_profile(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "players/delete_confirmation.html")
        self.assertEqual(response.context['object'], self.user.football_player)
    
    def test_authorized_POST_with_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse("user:detail", kwargs={
                "username": self.user.username,
            }),
            status_code=302,
            target_status_code=200,
        )

        ''' Making sure profile was deleted. '''
        self.assertFalse(FootballPlayer.objects.filter(user=self.user2).exists())

        ''' Making sure the right message is returned. '''
        the_message = list(response.context.get('messages'))[0]
        self.assertEqual(the_message.tags, "success")
        self.assertEqual(the_message.message, "Profilen har raderats!")

    def test_authorized_GET_without_profile(self):
        ''' Since the profile check occurs in the dispatch method,
        the same test result would apply to an authorized POST request
        without a profile. '''
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse("player:create", kwargs={"sport": "fotboll"}),
            status_code=302,
            target_status_code=200,
        )

    def test_authorized_GET_invalid_sport(self):
        ''' Since the piece of logic that handle invalid path converters are
        located in the dispatch method, the same test result would apply
        to an authorized POST request with an invalid sport. '''
        url = reverse("player:delete", kwargs={"sport": "asd"})
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    
class UpdatePlayerStatusTest(SetUpMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("player:update_status", kwargs={"sport": "fotboll"})

    def test_unauthorized_GET(self):
        ''' Since the piece of logic that handle authorization is
        located in the dispatch method, the same test result would
        apply to an unauthorized POST request. '''
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            "/logga-in/?next=/spelare/fotboll/uppdatera-status/",
            status_code=302,
            target_status_code=200,
        )

    def test_authorized_GET(self):
        ''' A GET request with or without profile should cause
        a http 405 error. '''
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_authorized_POST_with_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, follow=True)
        current_status = self.user.football_player.is_available
        self.assertRedirects(
            response,
            reverse("player:detail", kwargs={
                "sport": "fotboll",
                "username": self.user.username,
            })
        )

        ''' Making sure the status property was updated. '''
        self.user.football_player.refresh_from_db()
        self.assertNotEqual(current_status, self.user.football_player.is_available)

        ''' Making sure the right message is returned. '''
        the_message = list(response.context.get('messages'))[0]
        self.assertEqual(the_message.tags, "success")
        self.assertEqual(the_message.message, "Din tillgänglighet har uppdaterats!")

    def test_authorized_POST_without_profile(self):
        self.client.force_login(self.user2)
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("player:create", kwargs={"sport": "fotboll"}),
            status_code=302,
            target_status_code=200,
        )

    def test_authorized_GET_invalid_sport(self):
        ''' Since the piece of logic that handle invalid path converters are
        located in the dispatch method, the same test result would apply
        to an authorized POST request with an invalid sport. '''
        self.client.force_login(self.user2)
        url = reverse("player:update_status", kwargs={"sport": "asd"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


#   ---------------------------------------   #
#   ~~~~~~~~   TEST HISTORY VIEWS   ~~~~~~~   #            
#   ---------------------------------------   #


class CreatePlayerHistoryTest(SetUpTestDataMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("player:create_history", kwargs={"sport": "fotboll"})
    
    def test_unauthorized_GET(self):
        ''' Since the piece of logic that handle authorization is
        located in the dispatch method, the same test result would
        apply to an unauthorized POST request. '''
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            "/logga-in/?next=/spelare/fotboll/lagg-till-historik/",
            status_code=302,
            target_status_code=200,
        )

    def test_authorized_GET_with_profile(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "players/create_history.html")
        self.assertIsInstance(response.context['form'], FootballHistoryForm)

    def test_authorized_POST_with_profile(self):
        self.client.force_login(self.user)
        form_data = {
            "start_year": 2000,
            "end_year": 2001,
            "team_name": "Örebro SK",
        }
        response = self.client.post(self.url, form_data, follow=True)
        self.assertRedirects(
            response,
            reverse("player:detail", kwargs={
                "sport": "fotboll",
                "username": self.user.username,
            }),
            status_code=302,
            target_status_code=200,
        )

        ''' Making sure history entry was created, and that the player
        property was properly assigned. '''
        history_entry = FootballHistory.objects.last()
        self.assertEqual(history_entry.player, self.user.football_player)

        ''' Making sure the right message is returned. '''
        the_message = list(response.context.get('messages'))[0]
        self.assertEqual(the_message.tags, "success")
        self.assertEqual(the_message.message, "Historiken har skapats!")

    def test_authorized_GET_without_profile(self):
        ''' Since the profile check occurs in the dispatch method,
        the same test result would apply to an authorized POST request
        without a profile. '''
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            reverse("player:create", kwargs={"sport": "fotboll"}),
            status_code=302,
            target_status_code=200,
        )

    def test_authorized_GET_with_nonexistent_sport(self):
        ''' Since the piece of logic that handle invalid path converters are
        located in the dispatch method, the same test result would apply
        to an authorized POST request with an invalid sport. '''
        self.client.force_login(self.user)
        url = reverse("player:create_history", kwargs={"sport": "asd"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class UpdatePlayerHistoryTest(SetUpMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.history_entry = FootballHistory.objects.create(
            start_year=2000,
            end_year=2001,
            team_name="Örebro SK",
            player=self.user.football_player
        )
        self.url = reverse("player:update_history", kwargs={
            "sport": "fotboll",
            "id": self.history_entry.id,
        })

    def test_unauthorized_GET(self):
        ''' Since the piece of logic that handle authorization is
        located in the dispatch method, the same test result would
        apply to an unauthorized POST request. '''
        response = self.client.get(self.url)
        entry_id = self.history_entry.id
        self.assertRedirects(
            response,
            "/logga-in/?next=/spelare/fotboll/historik/{}/uppdatera/".format(entry_id),
            status_code=302,
            target_status_code=200
        )

    def test_authorized_GET_with_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "players/update_history.html")
        self.assertEqual(response.context['object'], self.history_entry)
    
    def test_authorized_POST_with_permission(self):
        self.client.force_login(self.user)
        form_data = {
            "start_year": 2000,
            "end_year": 2001,
            "team_name": "FC Barcelona",
        }
        response = self.client.post(self.url, form_data, follow=True)

        ''' Making sure history entry is updated. '''
        self.history_entry.refresh_from_db()
        self.assertEqual(self.history_entry.team_name, "FC Barcelona")

        ''' Making sure the right message is returned. '''
        the_message = list(response.context.get('messages'))[0]
        self.assertEqual(the_message.tags, "success")
        self.assertEqual(the_message.message, "Historiken har uppdaterats!")

    def test_authorized_GET_without_permission(self):
        ''' Since permission is checked in the dispatch method,
        the same test result would apply to an authorized POST request
        without a permmission. '''
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


    def test_authorized_GET_invalid_sport(self):
        ''' Since the piece of logic that handle invalid path converters are
        located in the dispatch method, the same test result would apply
        to an authorized POST request with an invalid sport. '''
        self.client.force_login(self.user)
        url = reverse("player:update_history", kwargs={
            "sport": "asd",
            "id": self.history_entry.id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_authorized_GET_invalid_id(self):
        ''' Since lookuping up and returning the object occurs in the dispatch
        method, the same test result would apply to an authorized GET request
        an invalid id. '''
        self.client.force_login(self.user)
        url = reverse("player:update_history", kwargs={
            "sport": "asd",
            "id": 2342342,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DeletePlayerHistoryTest(SetUpMixin, TestCase):
    
    def setUp(self):
        super().setUp()
        self.history_entry = FootballHistory.objects.create(
            start_year=2000,
            end_year=2001,
            team_name="Örebro SK",
            player=self.user.football_player
        )
        self.url = reverse("player:delete_history", kwargs={
            "sport": "fotboll",
            "id": self.history_entry.id,
        })

    def test_unauthorized_GET(self):
        ''' Since the piece of logic that handle authorization is
        located in the dispatch method, the same test result would
        apply to an unauthorized POST request. '''
        response = self.client.get(self.url)
        entry_id = self.history_entry.id
        self.assertRedirects(
            response,
            "/logga-in/?next=/spelare/fotboll/historik/{}/ta-bort/".format(entry_id),
            status_code=302,
            target_status_code=200,
        )

    def test_authorized_GET_with_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "players/delete_history_confirmation.html")
        self.assertEqual(response.context['object'], self.history_entry)

    def test_authorized_POST_with_permission(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse("player:detail", kwargs={
                "sport": "fotboll",
                "username": self.user.username,
            }),
            status_code=302,
            target_status_code=200,
        )

        ''' Making sure history entry is deleted. '''
        self.assertFalse(FootballHistory.objects.filter(player=self.user.football_player).exists())

        ''' Making sure the right message is returned. '''
        the_message = list(response.context.get('messages'))[0]
        self.assertEqual(the_message.tags, "success")
        self.assertEqual(the_message.message, "Historiken har raderats!")

    def test_authorized_GET_without_permission(self):
        ''' Since permission is checked in the dispatch method,
        the same test result would apply to an authorized POST request
        without a permmission. '''
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_authorized_GET_invalid_sport(self):
        ''' Since the piece of logic that handle invalid path converters are
        located in the dispatch method, the same test result would apply
        to an authorized POST request with an invalid sport. '''
        self.client.force_login(self.user)
        url = reverse("player:delete_history", kwargs={
            "sport": "asd",
            "id": self.history_entry.id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_authorized_GET_with_nonexistent_id(self):
        ''' Since lookuping up and returning the object occurs in the dispatch
        method, the same test result would apply to an authorized GET request
        an invalid id. '''
        self.client.force_login(self.user)
        url = reverse("player:delete_history", kwargs={
            "sport": "fotboll",
            "id": 99999,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)



