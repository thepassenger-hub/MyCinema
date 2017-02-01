from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from django.core.urlresolvers import resolve
from django.conf import settings
from django.core.files import File
from importlib import import_module

from django.http import HttpRequest
from django.template.loader import render_to_string
from movieapp_frontend.views import home_page, signup, login_page, \
    new_post_page, settings_page, change_name, change_password, profile_page, search_friends_page
from movie_app.models import MoviePost, Profile, Friendship
# Create your tests here.
import re
import os
# sys.path.append('/home/giulio/Desktop/Projects/movieapp/movieapp_backend')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieapp_backend.settings") # or whatever
import django
django.setup()



class HomePageTest(TestCase):

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

        User.objects.create_user('test','test','test')
        c.login(username='test', password='test')
        response = c.get('/')

        expected_html = render_to_string('movieapp_frontend/index.html')
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Homepage</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))

    def test_logout_link_logs_user_out_and_redirects_to_login(self):
        User.objects.create_user('aaaa', 'asd', 'asd')
        c = Client()
        c.login(username='aaaa', password='asd')
        response = c.get('/')
        self.assertEqual(200, response.status_code)
        response = c.get('/logout', follow=True)
        self.assertRedirects(response, '/login?next=/')
        response = c.get('/')
        self.assertEqual(302, response.status_code)

class SignUpPageTest(TransactionTestCase):
    @staticmethod
    def remove_csrf(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def test_sign_up_url_resolves_to_sign_up_view(self):
        found = resolve('/signup')
        self.assertEqual(found.func, signup)

    def test_sign_up_page_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        response = signup(request)
        expected_html = render_to_string('movieapp_frontend/signup.html')
        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Signup</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))
        self.assertEqual(self.remove_csrf(response.content.decode()), expected_html)

    def test_sign_up_page_can_post_new_users_and_redirects(self):
        # request = HttpRequest()
        c = Client()
        response = c.post('/signup/',
                          {'username': 'testusername',
                           'password': 'testpassword',
                           'verify_password': 'testpassword',
                           'email': 'testemail@email.com'}, follow=True)

        # engine = import_module(settings.SESSION_ENGINE)
        # session_key = None
        # request.session = engine.SessionStore(session_key)
        # request.method = 'POST'
        # request.POST['username'] = 'testusername'
        # request.POST['password'] = 'testpassword'
        # request.POST['verify_password'] = 'testpassword'
        # request.POST['email'] = 'testemail@email.com'
        # response = signup(request)
        user = User.objects.all()[0]
        self.assertEqual(user.username, 'testusername')
        self.assertEqual(user.email, 'testemail@email.com')
        friend = Profile.objects.get(user=user)
        self.assertEqual(0, len(friend.get_friends()))
        self.assertEqual(0, len(user.profile.get_friends()))
        # response.client = Client()

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
        self.assertEqual(1, len(users))

class LoginPageTest(TestCase):

    @staticmethod
    def remove_csrf(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def test_login_url_resolves_to_login_page_view(self):
        found = resolve('/login')
        self.assertEqual(found.func, login_page)

    def test_login_page_returns_correct_html(self):
        c = Client()
        response = c.get('/login', follow=True)
        expected_html = render_to_string('movieapp_frontend/login.html')

        self.assertTrue(response.content.startswith(b'<!DOCTYPE html>'))
        self.assertIn(b'<title>Login</title>', response.content)
        self.assertTrue(response.content.endswith(b'</html>'))
        self.assertEqual(self.remove_csrf(response.content.decode()), expected_html)

    def test_login_correctly_logs_user_in(self):
        User.objects.create_user('test', password='testpw')
        c = Client()
        response = c.post('/login', {'username': 'test', 'password': 'testpw' }, follow=True)
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)
        self.assertIn(b'<title>Homepage</title>', response.content)

    def test_cannot_loging_with_invalid_input(self):
        c = Client()
        response = c.post('/login', {'username': '', 'password': 'testpw' }, follow=True)
        self.assertIn('Invalid Username', response.content.decode())
        response = c.post('/login', {'username': 'test', 'password': '' }, follow=True)
        self.assertIn('Invalid Password', response.content.decode())
        response = c.post('/login', {'username': 'asd', 'password': 'testpw'}, follow=True)
        self.assertIn("Username doesn&#39;t exist", response.content.decode())
        User.objects.create_user('test', password='testpw')
        response = c.post('/login', {'username': 'test', 'password': 'testpw2'}, follow=True)
        self.assertIn("Wrong Password. Try again", response.content.decode())

class SendPostPageTest(TestCase):

    def create_three_friends(self):
        aaa = User.objects.create_user('aaa', password='aaa')
        Profile(user=aaa).save()
        bbb = User.objects.create_user('bbb', password='aaa')
        Profile(user=bbb).save()
        ccc = User.objects.create_user('ccc', password='aaa')
        Profile(user=ccc).save()
        friendship = Friendship()
        friendship.creator = aaa
        friendship.friend = bbb
        friendship.save()
        friendship = Friendship()
        friendship.creator = aaa
        friendship.friend = ccc
        friendship.save()
        friendship = Friendship()
        friendship.creator = bbb
        friendship.friend = ccc
        friendship.save()

        return aaa,bbb,ccc

    def aaa_sends_movie_post(self, send_to='bbb,ccc'):
        c = Client()
        c.login(username='aaa', password='aaa')
        movie_post = {
            'title': 'Ip Man',
            'image_url': 'url to image',
            'url': 'http://www.imdb.com/title/tt1220719/',
            'rating': 8,
            'content': 'One of the best fighting movies I have ever seen.',
            'send_to': send_to,
        }

        response = c.post('/newpost', movie_post)
        return response


    @staticmethod
    def remove_csrf(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def test_new_post_url_resolves_to_new_post_page_view(self):
        found = resolve('/newpost')
        self.assertEqual(found.func, new_post_page)

    def test_new_post_url_returns_correct_template(self):
        c = Client()
        User.objects.create_user('aaa', password='aaa')
        c.login(username='aaa', password='aaa')
        response = c.get('/newpost')
        expected_html = render_to_string('movieapp_frontend/newpost.html')
        self.assertEqual(self.remove_csrf(response.content.decode()), expected_html)

    def test_sending_post_to_view_creates_post_in_db_and_is_received(self):

        aaa,bbb,ccc = self.create_three_friends()
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
        aaa,bbb,ccc = self.create_three_friends()

        self.assertEqual(aaa.profile.get_friends(), [bbb, ccc])
        self.assertEqual(bbb.profile.get_friends(), [aaa, ccc])
        self.assertEqual(ccc.profile.get_friends(), [aaa, bbb])
        Friendship.objects.get(creator=bbb).delete()
        self.assertEqual(ccc.profile.get_friends(), [aaa])
        User.objects.get(username='aaa').delete()
        self.assertEqual(len(ccc.profile.get_friends()), 0)
        self.assertEqual(0, len(Friendship.objects.all()))

    def test_deleting_users_and_post_working_correctly(self):
        aaa,bbb,ccc = self.create_three_friends()
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
        c = Client()
        User.objects.create_user('aaa', password='aaa')
        c.login(username='aaa', password='aaa')
        response = c.post('/newpost', {'title': ''})
        self.assertIn('This field is required', response.content.decode())
        response = c.post('/newpost', {'title': 't', 'rating': ''})
        self.assertIn('This field is required', response.content.decode())

    def test_cannot_send_to_user_that_isnt_my_friend(self):
        aaa,bbb,ccc = self.create_three_friends()
        bbb.friend_set.all()[0].delete()
        self.assertNotIn(bbb, aaa.profile.get_friends())
        self.aaa_sends_movie_post()
        self.assertEqual(0, len(bbb.received_posts.all()))
        self.assertEqual(1, len(ccc.received_posts.all()))

    def test_empty_send_to_sends_to_all_friends(self):
        aaa,bbb,ccc = self.create_three_friends()
        ddd = User.objects.create_user(username='ddd', password='whocares')
        self.aaa_sends_movie_post(send_to='')
        movie = MoviePost.objects.all()[0]
        self.assertEqual(movie, aaa.posts.all()[0])
        self.assertEqual(movie, bbb.received_posts.all()[0])
        self.assertEqual(movie, ccc.received_posts.all()[0])
        self.assertEqual(0, len(ddd.received_posts.all()))


class SettingsPageTest(TestCase):
    def create_three_friends(self):
        aaa = User.objects.create_user('aaa', password='aaa')
        Profile(user=aaa).save()
        bbb = User.objects.create_user('bbb', password='aaa')
        Profile(user=bbb).save()
        ccc = User.objects.create_user('ccc', password='aaa')
        Profile(user=ccc).save()
        friendship = Friendship()
        friendship.creator = aaa
        friendship.friend = bbb
        friendship.save()
        friendship = Friendship()
        friendship.creator = aaa
        friendship.friend = ccc
        friendship.save()
        friendship = Friendship()
        friendship.creator = bbb
        friendship.friend = ccc
        friendship.save()

        return aaa,bbb,ccc

    @staticmethod
    def remove_csrf(html_code):
        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def create_logged_in_client(self):
        aaa = User.objects.create_user('aaa', password='aaa')
        Profile(user=aaa).save()
        c = Client()
        c.login(username='aaa', password='aaa')
        return c,aaa

    def test_settings_url_resolves_to_correct_view(self):
        found = resolve('/settings')
        self.assertEqual(found.func, settings_page)

    def test_settings_page_cannot_enter_if_not_logged_in(self):
        c = Client()
        response = c.get('/settings')
        self.assertEqual(response.status_code, 302)
        response = c.get('/settings', follow=True)
        self.assertRedirects(response, '/login?next=/settings', status_code=302, target_status_code=200)

    def test_authenticated_user_can_view_correct_html(self):
        c,aaa = self.create_logged_in_client()
        response = c.get('/settings')
        self.assertEqual(200, response.status_code)
        self.assertIn('Settings', response.content.decode())
        # rendered_template = render_to_string('movieapp_frontend/settings.html')
        # self.assertEqual(self.remove_csrf(response.content.decode()), rendered_template)

    def test_user_change_name_updates_name_in_db(self):
        c,aaa = self.create_logged_in_client()
        self.assertEqual(aaa.profile.name, None)
        request = HttpRequest()
        request.method = 'POST'
        request.user = aaa
        request.POST['name'] = ''
        response = change_name(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings')
        request.POST['name'] = 'My new cool name'
        response = change_name(request)
        self.assertEqual(aaa.profile.name, 'My new cool name')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings')
        request = HttpRequest()
        request.method = 'GET'
        request.user = aaa
        response = settings_page(request)
        self.assertIn('My new cool name', response.content.decode())

    def test_user_change_password_updates_pw_in_db_and_current_session_cookie(self):
        c,aaa = self.create_logged_in_client()
        old_password = aaa.password
        # request = HttpRequest()
        # engine = import_module(settings.SESSION_ENGINE)
        # session_key = None
        response = c.post('/settings/change_password/',
                          {'new_password': '',}, follow=True)
        # request.session = engine.SessionStore(session_key)
        # request.method = 'POST'
        # request.user = aaa
        # request.POST['new_password'] = ''
        # response = change_password(request)
        # self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/settings')
        # print (response.url)
        self.assertIn('This field is required.', response.content.decode())
        response = c.post('/settings/change_password/',
                          {'new_password': 'mynewpassword', }, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('This field is required.', response.content.decode())
        response = c.post('/settings/change_password/',
                          {'new_password': 'aa',
                           'verify_new_password': 'aa'}, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('between 3 and 20', response.content.decode())
        response = c.post('/settings/change_password/',
                          {'new_password': 'mynewpassword',
                           'verify_new_password': 'mynewpassword'}, follow=True)
        aaa = User.objects.get(username='aaa')
        self.assertNotEqual(old_password, aaa.password)
        self.assertNotEqual(aaa.password, 'mynewpassword')
        self.assertIn('pbkdf2_sha256', aaa.password)
        self.assertRedirects(response, '/settings')
        self.assertIn('Password change successful', response.content.decode())
        user = get_user(c)
        self.assertTrue(user.is_authenticated)

    def test_can_upload_new_avatar(self):
        c,aaa = self.create_logged_in_client()
        self.assertFalse(aaa.profile.avatar)

        with open('utils/avatar_2.png', 'rb') as fp:

            response = c.post('/settings/change_avatar/', {
                'avatar': fp,
            }, follow=True, format='multipart')
        self.assertRedirects(response, '/settings')
        aaa = User.objects.get(username='aaa')
        self.assertTrue(aaa.profile.avatar)
        with open('utils/avatar_600.png', 'rb') as fp:
            response = c.post('/settings/change_avatar/', {
                'avatar': fp,
            }, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('max 500px', response.content.decode())
        with open('utils/avatar_600.bitmap', 'rb') as fp:
            response = c.post('/settings/change_avatar/', {
                'avatar': fp,
            }, follow=True)
        self.assertRedirects(response, '/settings')
        self.assertIn('Only *.gif', response.content.decode())

    def test_can_see_all_friends(self):
        aaa,bbb,ccc = self.create_three_friends()
        c = Client()
        c.login(username='aaa', password='aaa')
        response = c.get('/settings')
        self.assertIn('bbb', response.content.decode())
        self.assertIn('ccc', response.content.decode())
        f = Friendship.objects.get(creator=aaa, friend=ccc)
        f.delete()
        response = c.get('/settings')
        self.assertIn('bbb', response.content.decode())
        self.assertNotIn('ccc', response.content.decode())

    def test_can_delete_account(self):
        c,aaa = self.create_logged_in_client()
        self.assertTrue(aaa.is_active)
        response = c.get('/settings/delete_account/', follow=True)
        self.assertFalse(User.objects.get(username='aaa').is_active)
        self.assertRedirects(response, '/login?next=/')

class SearchFriendsPageTest(TestCase):
    def create_logged_in_client(self):
        aaa = User.objects.create_user('aaa', password='aaa')
        Profile(user=aaa).save()
        c = Client()
        c.login(username='aaa', password='aaa')
        return c,aaa

    def test_search_friends_page_url_resolves_correct_view(self):
        found = resolve('/search_friends/')
        self.assertEqual(found.func, search_friends_page)

    def test_search_friends_in_home_page_calls_view_and_result_is_shown(self):
        c, aaa = self.create_logged_in_client()
        bbb = User.objects.create_user(username='bbb', password='bbb')
        p = Profile(user=bbb)
        p.name = 'Test Name'
        p.avatar = File(open('utils/avatar_2.png', 'rb'))
        p.save()
        response = c.get('/search_friends/?username=bbb')
        self.assertIn('bbb', response.content.decode())
        self.assertIn('Test Name', response.content.decode())
        self.assertIn('avatar_2', response.content.decode())

class ProfilePageTest(TestCase):

    def create_logged_in_client(self):
        aaa = User.objects.create_user('aaa', password='aaa')
        Profile(user=aaa).save()
        c = Client()
        c.login(username='aaa', password='aaa')
        return c,aaa

    def test_profile_page_url_resolves_correct_view(self):
        found = resolve('/profile/randomuser/')
        self.assertEqual(found.func, profile_page)

    def test_can_view_other_user_profile(self):
        c, aaa = self.create_logged_in_client()
        bbb = User.objects.create_user(username='bbb', password='bbb')
        p = Profile(user=bbb)
        p.name = 'Test Name'
        p.avatar = File(open('utils/avatar_2.png', 'rb'))
        p.save()
        response = c.get('/profile/bbb/')
        self.assertEqual(200, response.status_code)








