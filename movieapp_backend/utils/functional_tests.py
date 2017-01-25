from selenium import webdriver
from django.test import LiveServerTestCase
import unittest
import os, sys
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieapp_backend.settings") # or whatever
import django
django.setup()

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
        self.assertIn('testusername', self.browser.title)
        self.fail("finish the test")

if __name__ == '__main__':
    unittest.main(warnings='ignore')
