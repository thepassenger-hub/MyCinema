from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.conf import settings
from importlib import import_module

from django.http import HttpRequest
from django.template.loader import render_to_string
from movieapp_frontend.views import home_page, signup, login_page
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
        self.assertEqual(response.content.decode(), expected_html)

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







