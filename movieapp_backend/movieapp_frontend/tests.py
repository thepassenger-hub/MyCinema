from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve

from django.http import HttpRequest
from django.template.loader import render_to_string
from movieapp_frontend.views import home_page, signup
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
        request = HttpRequest()
        request.method = 'POST'
        request.POST['username'] = 'testusername'
        request.POST['password'] = 'testpassword'
        request.POST['verify_password'] = 'testpassword'
        request.POST['email'] = 'testemail@email.com'
        response = signup(request)
        user = User.objects.all()[0]
        self.assertEqual(user.username, 'testusername')
        self.assertEqual(user.email, 'testemail@email.com')
        response.client = Client()
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)

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



