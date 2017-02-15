import os
import re
from importlib import import_module
import django
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.core.files import File
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase, TransactionTestCase, Client

from movie_app.models import MoviePost, Profile, Friendship, FriendshipRequest
from movieapp_frontend.views import home_page, signup, login_page, \
    new_post_page, settings_page, change_name, profile_page, search_friends_page

# sys.path.append('/home/giulio/Desktop/Projects/movieapp/movieapp_backend')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieapp_backend.settings")  # or whatever
django.setup()


def inherit_test_case(base_class):
    class BaseTestCase(base_class):
        def setUp(self):
            self.all_users = []
            self.aaa = User.objects.create_user('aaa', password='aaa')
            Profile(user=self.aaa).save()
            self.bbb = User.objects.create_user(username='bbb', password='bbb')
            Profile(user=self.bbb).save()
            self.all_users.append(self.aaa)
            self.all_users.append(self.bbb)
            self.c = Client()
            self.c.login(username='aaa', password='aaa')

        def create_third_user(self):
            self.ccc = User.objects.create_user('ccc', password='ccc')
            Profile(user=self.ccc).save()
            self.all_users.append(self.ccc)

        def make_all_users_friends(self):

            Friendship.objects.create(creator=self.aaa, friend=self.bbb)

            try:
                Friendship.objects.create(creator=self.bbb, friend=self.ccc)
            except:
                pass

            try:
                Friendship.objects.create(creator=self.aaa, friend=self.ccc)
            except:
                pass

        def aaa_sends_movie_post(self, send_to='bbb,ccc'):
            movie_post = {
                'title': 'Ip Man',
                'image_url': 'url to image',
                'url': 'http://www.imdb.com/title/tt1220719/',
                'rating': 8,
                'comment': 'One of the best fighting movies I have ever seen.',
                'send_to': send_to,
            }

            response = self.c.post('/newpost', movie_post)
            return response

        def tearDown(self):
            self.c.logout()

        def create_friendship_request(self, user1, user2):
            f = FriendshipRequest.objects.create(from_user=user1, to_user=user2)
            return f

        def create_friendship(self, user1, user2):
            f = Friendship.objects.create(creator=user1, friend=user2)
            return f

    return BaseTestCase


class HomePageTest(inherit_test_case(TestCase)):
    @staticmethod
    def remove_csrf(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        c = Client()
        response = c.get('/', follow=True)
        # expected_html = render_to_string('movieapp_frontend/index.html')
        self.assertRedirects(response, '/login?next=/')
        expected_html = render_to_string('movieapp_frontend/login.html')

        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Login</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))
        self.assertEqual(self.remove_csrf(response.content.decode()), expected_html)

        response = self.c.get('/')

        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Homepage</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))

    def test_logout_link_logs_user_out_and_redirects_to_login(self):
        response = self.c.get('/')
        self.assertEqual(200, response.status_code)
        response = self.c.get('/logout', follow=True)
        self.assertRedirects(response, '/login?next=/')
        response = self.c.get('/')
        self.assertEqual(302, response.status_code)


class SignUpPageTest(inherit_test_case(TransactionTestCase)):
    @staticmethod
    def remove_csrf(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def test_sign_up_url_resolves_to_sign_up_view(self):
        found = resolve('/signup')
        self.assertEqual(found.func, signup)

    def test_sign_up_page_returns_correct_html(self):
        response = self.c.get('/signup')
        render_to_string('movieapp_frontend/signup.html')
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Signup</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))
        # self.assertEqual(self.remove_csrf(response.content.decode()), expected_html)

    def test_sign_up_page_can_post_new_users_and_redirects(self):
        response = self.c.post('/signup/',
                               {'username': 'testusername',
                                'password': 'testpassword',
                                'verify_password': 'testpassword',
                                'email': 'testemail@email.com'}, follow=True)

        user = User.objects.get(username='testusername')
        self.assertEqual(user.username, 'testusername')
        self.assertEqual(user.email, 'testemail@email.com')
        self.assertEqual(0, len(user.profile.get_friends()))

        self.assertRedirects(response, '/', status_code=302, target_status_code=200)
        self.assertIn(b'<title>Homepage</title>', response.content)

    def test_sign_up_not_accepting_empty_values(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['username'] = ''
        response = signup(request)
        self.assertIn('Invalid Username', response.content.decode())
        request.POST['username'] = 'testusername'
        request.POST['password'] = ''
        response = signup(request)
        self.assertIn('Invalid Password', response.content.decode())
        request.POST['password'] = 'testpassword'
        request.POST['email'] = ''
        response = signup(request)
        self.assertIn('Invalid Email', response.content.decode())
        request.POST['verify_password'] = 'testpassword1'
        request.POST['email'] = 'testemail@email.com'
        response = signup(request)
        self.assertIn('Passwords don&#39;t match', response.content.decode())

    def test_sign_up_not_accepting_double_username(self):
        request = HttpRequest()
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        request.session = engine.SessionStore(session_key)
        request.method = 'POST'
        request.POST['username'] = 'testusername'
        request.POST['password'] = 'testpassword'
        request.POST['verify_password'] = 'testpassword'
        request.POST['email'] = 'testemail@email.com'
        signup(request)
        response = signup(request)
        self.assertIn('Username already exists', response.content.decode())
        users = User.objects.all()
        self.assertEqual(3, len(users))


class LoginPageTest(inherit_test_case(TestCase)):
    @staticmethod
    def remove_csrf(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def test_login_url_resolves_to_login_page_view(self):
        found = resolve('/login')
        self.assertEqual(found.func, login_page)

    def test_login_page_returns_correct_html(self):
        response = self.c.get('/login', follow=True)

        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Login</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))
        # self.assertEqual(self.remove_csrf(response.content.decode()), expected_html)

    def test_login_correctly_logs_user_in(self):
        self.c.logout()
        response = self.c.post('/login', {'username': 'aaa', 'password': 'aaa'}, follow=True)
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)
        self.assertIn(b'<title>Homepage</title>', response.content)

    def test_cannot_loging_with_invalid_input(self):
        c = Client()
        response = c.post('/login', {'username': '', 'password': 'testpw'}, follow=True)
        self.assertIn('Invalid Username', response.content.decode())
        response = c.post('/login', {'username': 'test', 'password': ''}, follow=True)
        self.assertIn('Invalid Password', response.content.decode())
        response = c.post('/login', {'username': 'asd', 'password': 'testpw'}, follow=True)
        self.assertIn("Username doesn&#39;t exist", response.content.decode())
        response = c.post('/login', {'username': 'aaa', 'password': 'testpw2'}, follow=True)
        self.assertIn("Wrong Password. Try again", response.content.decode())


class SendPostPageTest(inherit_test_case(TestCase)):
    def create_three_friends(self):
        self.create_third_user()
        self.make_all_users_friends()

        return self.aaa, self.bbb, self.ccc

    @staticmethod
    def remove_csrf(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def test_new_post_url_resolves_to_new_post_page_view(self):
        found = resolve('/newpost')
        self.assertEqual(found.func, new_post_page)

    def test_sending_post_to_view_creates_post_in_db_and_is_received(self):
        aaa, bbb, ccc = self.create_three_friends()
        response = self.aaa_sends_movie_post()

        movie = MoviePost.objects.all()
        self.assertEqual(1, len(movie))
        self.assertEqual('Ip Man', movie[0].title)
        self.assertEqual('url to image', movie[0].image_url)
        self.assertEqual('One of the best fighting movies I have ever seen.', movie[0].content)
        self.assertEqual(aaa, movie[0].user)
        self.assertEqual(movie[0], aaa.posts.all()[0])
        self.assertEqual(bbb.received_posts.all()[0], movie[0])
        self.assertEqual(ccc.received_posts.all()[0], movie[0])
        self.assertIn('Post Sent', response.content.decode())

    def test_user_friendship_is_working(self):
        aaa, bbb, ccc = self.create_three_friends()

        self.assertEqual(aaa.profile.get_friends(), [bbb, ccc])
        self.assertTrue(aaa.profile.is_friend(bbb))
        self.assertEqual(bbb.profile.get_friends(), [aaa, ccc])
        self.assertTrue(aaa.profile.is_friend(ccc))
        self.assertEqual(ccc.profile.get_friends(), [bbb, aaa])
        self.assertTrue(ccc.profile.is_friend(bbb))
        Friendship.objects.get(creator=bbb).delete()
        self.assertEqual(ccc.profile.get_friends(), [aaa])
        self.assertFalse(bbb.profile.is_friend(ccc))
        User.objects.get(username='aaa').delete()
        self.assertEqual(len(ccc.profile.get_friends()), 0)
        self.assertEqual(0, len(Friendship.objects.all()))

    def test_deleting_users_and_post_working_correctly(self):
        aaa, bbb, ccc = self.create_three_friends()
        self.aaa_sends_movie_post()
        bbb.delete()
        movie = MoviePost.objects.all()
        self.assertEqual(1, len(movie))
        self.assertEqual(1, len(movie[0].send_to.all()))
        movie.delete()
        self.assertEqual(0, len(aaa.posts.all()))
        self.assertEqual(0, len(ccc.received_posts.all()))
        self.aaa_sends_movie_post()
        aaa.delete()
        self.assertEqual(0, len(MoviePost.objects.all()))

    def test_cannot_send_post_with_wrong_inputs(self):
        response = self.c.post('/newpost', {'title': ''})
        self.assertIn('This field is required', response.content.decode())
        response = self.c.post('/newpost', {'title': 't', 'rating': ''})
        self.assertIn('This field is required', response.content.decode())

    def test_cannot_send_to_user_that_isnt_my_friend(self):
        aaa, bbb, ccc = self.create_three_friends()
        bbb.friend_set.all()[0].delete()
        self.assertNotIn(bbb, aaa.profile.get_friends())
        self.aaa_sends_movie_post()
        self.assertEqual(0, len(bbb.received_posts.all()))
        self.assertEqual(1, len(ccc.received_posts.all()))

    def test_empty_send_to_sends_to_all_friends(self):
        aaa, bbb, ccc = self.create_three_friends()
        ddd = User.objects.create_user(username='ddd', password='whocares')
        self.aaa_sends_movie_post(send_to='')
        movie = MoviePost.objects.all()[0]
        self.assertEqual(movie, aaa.posts.all()[0])
        self.assertEqual(movie, bbb.received_posts.all()[0])
        self.assertEqual(movie, ccc.received_posts.all()[0])
        self.assertEqual(0, len(ddd.received_posts.all()))


class SettingsPageTest(inherit_test_case(TestCase)):
    def create_logged_in_client(self):
        aaa = User.objects.create_user('aaa', password='aaa')
        Profile(user=aaa).save()
        c = Client()
        c.login(username='aaa', password='aaa')
        return c, aaa

    def test_settings_url_resolves_to_correct_view(self):
        found = resolve('/settings')
        self.assertEqual(found.func, settings_page)

    def test_settings_page_cannot_enter_if_not_logged_in(self):
        self.c.logout()
        response = self.c.get('/settings', follow=True)
        self.assertRedirects(response, '/login?next=/settings', status_code=302, target_status_code=200)

    def test_authenticated_user_can_view_correct_html(self):
        response = self.c.get('/settings')
        self.assertEqual(200, response.status_code)
        self.assertIn('Settings', response.content.decode())

    def test_user_change_name_updates_name_in_db(self):
        self.assertEqual(self.aaa.profile.name, None)
        request = HttpRequest()
        request.method = 'POST'
        request.user = self.aaa
        request.POST['name'] = ''
        response = change_name(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings')
        request.POST['name'] = 'My new cool name'
        response = change_name(request)
        self.assertEqual(self.aaa.profile.name, 'My new cool name')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings')
        request = HttpRequest()
        request.method = 'GET'
        request.user = self.aaa
        response = settings_page(request)
        self.assertIn('My new cool name', response.content.decode())

    def test_user_change_password_updates_pw_in_db_and_current_session_cookie(self):
        old_password = self.aaa.password
        response = self.c.post('/settings/change_password/',
                               {'new_password': '', }, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('This field is required.', response.content.decode())
        response = self.c.post('/settings/change_password/',
                               {'new_password': 'mynewpassword', }, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('This field is required.', response.content.decode())
        response = self.c.post('/settings/change_password/',
                               {'new_password': 'aa',
                                'verify_new_password': 'aa'}, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('between 3 and 20', response.content.decode())
        response = self.c.post('/settings/change_password/',
                               {'new_password': 'mynewpassword',
                                'verify_new_password': 'mynewpassword'}, follow=True)
        aaa = User.objects.get(username='aaa')
        self.assertNotEqual(old_password, aaa.password)
        self.assertNotEqual(aaa.password, 'mynewpassword')
        self.assertIn('pbkdf2_sha256', aaa.password)
        self.assertRedirects(response, '/settings')
        self.assertIn('Password change successful', response.content.decode())
        user = get_user(self.c)
        self.assertTrue(user.is_authenticated)

    def test_can_upload_new_avatar(self):
        self.assertEqual(self.aaa.profile.avatar.url, '/avatar_images/avatar.svg')

        with open('utils/avatar_2.png', 'rb') as fp:
            response = self.c.post('/settings/change_avatar/', {
                'avatar': fp,
            }, follow=True, format='multipart')
        self.assertRedirects(response, '/settings')
        aaa = User.objects.get(username='aaa')
        self.assertTrue(aaa.profile.avatar)
        with open('utils/avatar_600.png', 'rb') as fp:
            response = self.c.post('/settings/change_avatar/', {
                'avatar': fp,
            }, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('max 500px', response.content.decode())
        with open('utils/avatar_600.bitmap', 'rb') as fp:
            response = self.c.post('/settings/change_avatar/', {
                'avatar': fp,
            }, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('Only *.gif', response.content.decode())

    def test_can_see_all_friends(self):
        self.create_third_user()
        self.make_all_users_friends()
        response = self.c.get('/settings')
        self.assertIn('bbb', response.content.decode())
        self.assertIn('ccc', response.content.decode())
        f = Friendship.objects.get(creator=self.aaa, friend=self.ccc)
        f.delete()
        response = self.c.get('/settings')
        self.assertIn('bbb', response.content.decode())
        self.assertNotIn('ccc', response.content.decode())

    def test_can_delete_account(self):
        self.assertTrue(self.aaa.is_active)
        response = self.c.post('/settings/delete_account/', follow=True)
        self.assertFalse(User.objects.get(username='aaa').is_active)
        self.assertRedirects(response, '/login?next=/')


class SearchFriendsPageTest(inherit_test_case(TestCase)):
    def test_search_friends_page_url_resolves_correct_view(self):
        found = resolve('/search_friends/')
        self.assertEqual(found.func, search_friends_page)

    def test_search_friends_in_home_page_calls_view_and_result_is_shown(self):
        p = self.bbb.profile
        p.name = 'Test Name'
        p.avatar = File(open('utils/avatar_2.png', 'rb'))
        p.save()
        response = self.c.get('/search_friends/?username=bbb')
        self.assertIn('bbb', response.content.decode())
        self.assertIn('Test Name', response.content.decode())
        self.assertIn('avatar_2', response.content.decode())


class ProfilePageTest(inherit_test_case(TestCase)):
    def test_profile_page_url_resolves_correct_view(self):
        found = resolve('/profile/randomuser/')
        self.assertEqual(found.func, profile_page)

    def test_can_view_other_user_profile(self):
        response = self.c.get('/profile/bbb/')
        self.assertEqual(200, response.status_code)

    def test_can_send_friend_request(self):
        self.assertEqual(0, len(FriendshipRequest.objects.all()))
        response = self.c.post('/friend/add/bbb/', follow=True)
        self.assertEqual(1, len(FriendshipRequest.objects.all()))
        friend_request = FriendshipRequest.objects.all()[0]
        self.assertEqual(self.aaa, friend_request.from_user)
        self.assertEqual(self.bbb, friend_request.to_user)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Friend Request Sent', response.content.decode())

    def test_can_accept_friend_request(self):
        self.assertNotIn(self.aaa, self.bbb.profile.get_friends())
        f1 = self.create_friendship_request(self.aaa, self.bbb)
        self.create_third_user()
        f2 = self.create_friendship_request(self.ccc, self.bbb)
        self.c.logout()
        self.c.login(username='bbb', password='bbb')
        response = self.c.post('/friend/accept/%d/' % f1.pk, follow=True)
        self.assertEqual(1, len(self.bbb.profile.get_friends()))
        self.assertIn(self.aaa, self.bbb.profile.get_friends())
        self.assertTrue(Friendship.objects.filter(creator=self.aaa, friend=self.bbb))
        self.assertIn('aaa', response.content.decode())
        self.c.post('/friend/reject/%d/' % f2.pk)
        self.assertEqual(1, len(self.bbb.profile.get_friends()))
        self.assertNotIn(self.ccc, self.bbb.profile.get_friends())
        self.assertFalse(Friendship.objects.filter(creator=self.ccc, friend=self.bbb))

    def test_cannot_send_send_more_than_one_request_to_same_user(self):
        self.c.post('/friend/add/bbb/', follow=True)
        response = self.c.post('/friend/add/bbb/', follow=True)
        self.assertIn('A friend request is already pending.', response.content.decode())
        self.assertEqual(1, len(FriendshipRequest.objects.all()))

    def test_cannot_add_yourself(self):
        response = self.c.post('/friend/add/aaa/', follow=True)
        self.assertIn("You can&#39;t add yourself.", response.content.decode())
        self.assertFalse(self.aaa.profile.is_friend(self.aaa))

    def test_cannot_send_friend_request_if_already_friends(self):
        self.create_third_user()
        self.create_friendship(self.aaa, self.ccc)
        response = self.c.post('/friend/add/ccc/', follow=True)
        self.assertIn('You are already friends.', response.content.decode())
        self.assertFalse(FriendshipRequest.objects.all())

    def test_can_remove_users_from_friendlist_and_relation_are_deleted(self):
        self.make_all_users_friends()
        self.aaa_sends_movie_post()
        self.assertEqual(1, len(self.bbb.received_posts.all()))
        self.c.post('/friend/delete/bbb/', follow=True)
        self.assertNotIn(self.bbb, self.aaa.profile.get_friends())
        self.assertEqual(0, len(self.bbb.received_posts.all()))

