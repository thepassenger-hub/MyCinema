from selenium import webdriver
from django.test import LiveServerTestCase
import unittest
import os, sys
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieapp_backend.settings") # or whatever
import django
django.setup()
from django.contrib.auth.models import User


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_login_page_on_first_visit(self):
        self.browser.get(self.live_server_url)

        self.assertIn('Login', self.browser.title)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        self.assertEqual(username.get_attribute('placeholder'), 'Username')
        self.assertEqual(password.get_attribute('placeholder'), 'Password')
        self.browser.find_element_by_id('login_button')
        sign_in = self.browser.find_element_by_id('sign_in_url')
        sign_in.click()

    def test_can_register_new_account(self):
        self.browser.get('%s%s' % (self.live_server_url, '/signup'))
        self.assertIn('Signup', self.browser.title)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        verify_password = self.browser.find_element_by_id('verify_password_input')
        email = self.browser.find_element_by_id('email_input')
        username.send_keys('testusername')
        password.send_keys('testpassword')
        verify_password.send_keys('testpassword')
        email.send_keys('testmail@mail.com')
        button = self.browser.find_element_by_id('signup_button')
        button.click()
        import time
        time.sleep(2)
        self.assertIn('Homepage', self.browser.title)

    def test_home_page_when_logged(self):
        User.objects.create_user('aaaa', password='asdasdasd')
        # print (User.objects.all())
        self.browser.get(self.live_server_url)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        username.send_keys('aaaa')
        password.send_keys('asdasdasd')
        login = self.browser.find_element_by_id('login_button')
        login.click()
        import time
        time.sleep(1)
        self.assertIn('Homepage', self.browser.title)
        self.browser.find_element_by_id('username')
        self.browser.find_element_by_id('logout_url')
        send_post = self.browser.find_element_by_id('send_post')
        send_post.click()
        time.sleep(1)
        self.assertIn('New Post', self.browser.title)
        title = self.browser.find_element_by_id('title_input')
        img = self.browser.find_element_by_id('img_input')
        url = self.browser.find_element_by_id('url_input')
        rating = self.browser.find_element_by_id('rating_input')
        comment = self.browser.find_element_by_id('comment_textarea')
        send_to = self.browser.find_element_by_id('send_to_button')
        send_post = self.browser.find_element_by_id('send_post_button')
        title.send_keys('Ip Man')
        img.send_keys('url to image')
        url.send_keys('http://www.imdb.com/title/tt1220719/')
        rating.send_keys('8')
        comment.send_keys('One of the best fighting movies I have ever seen.')
        send_to.click()
        send_post.click()
        # Check Settings page. No redirects because I'm still logged in.
        settings = self.browser.find_element_by_id('settings_link')
        settings.click()
        time.sleep(1)
        self.assertIn('Settings', self.browser.title)
        self.browser.find_element_by_id('change_name_form')
        change_name = self.browser.find_element_by_id('change_name_input')
        change_name.send_keys('My new cool name')
        submit_change = self.browser.find_element_by_id('submit_change_name_button')
        submit_change.click()
        time.sleep(1)
        self.browser.find_element_by_id('name_tag')
        self.browser.find_element_by_id('change_name_button')
        self.browser.find_element_by_id('avatar')
        self.browser.find_element_by_id('change_avatar_button')
        self.browser.find_element_by_id('friends_list')
        self.browser.find_element_by_id('change_password_button')
        self.browser.find_element_by_id('delete_account_button')


        self.fail("finish the test")

if __name__ == '__main__':
    unittest.main(warnings='ignore')
