from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.conf import settings
from importlib import import_module

from django.http import HttpRequest
from django.template.loader import render_to_string
from movieapp_frontend.views import home_page, signup, login_page, new_post_page
from movie_app.models import MoviePost, Friends, Friendship
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
        friend = Friends.objects.get(user=user)
        self.assertEqual(0, len(friend.get_all()))
        self.assertEqual(0, len(user.friends.get_all()))
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
        Friends(user=aaa).save()
        bbb = User.objects.create_user('bbb', password='aaa')
        Friends(user=bbb).save()
        ccc = User.objects.create_user('ccc', password='aaa')
        Friends(user=ccc).save()
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

    def test_sending_post_to_view_creates_post_in_db(self):

        self.create_three_friends()
        c = Client()
        aaa = User.objects.get(username='aaa')
        bbb = User.objects.get(username='bbb')
        ccc = User.objects.get(username='ccc')

        c.login(username='aaa', password='aaa')
        movie_post = {
            'title': 'Ip Man',
            'image_url': 'url to image',
            'url': 'http://www.imdb.com/title/tt1220719/',
            'rating': 8,
            'content': 'One of the best fighting movies I have ever seen.',
            'send_to': 'bbb,ccc',
        }
        response = c.post('/newpost', movie_post)

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
        User.objects.get(username='aaa').delete()
        self.assertEqual(0, len(MoviePost.objects.all()))

    def test_cannot_send_post_with_wrong_inputs(self):
        c = Client()
        User.objects.create_user('aaa', password='aaa')
        c.login(username='aaa', password='aaa')
        response = c.post('/newpost', {'title': ''})
        self.assertIn('This field is required', response.content.decode())
        response = c.post('/newpost', {'title': 't', 'rating': ''})
        self.assertIn('This field is required', response.content.decode())

    def test_user_friendship_is_working(self):
        self.create_three_friends()
        aaa = User.objects.get(username='aaa')
        bbb = User.objects.get(username='bbb')
        ccc = User.objects.get(username='ccc')
        self.assertEqual(aaa.friends.get_all(), [bbb, ccc])
        self.assertEqual(bbb.friends.get_all(), [aaa, ccc])
        self.assertEqual(ccc.friends.get_all(), [aaa, bbb])













