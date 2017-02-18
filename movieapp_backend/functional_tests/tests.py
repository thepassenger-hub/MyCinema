from selenium import webdriver
import django
from django.test import LiveServerTestCase
import unittest
import os
import sys
import time

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieapp_backend.settings")  # or whatever
django.setup()


class NewVisitorTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):

        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]  #
                return

        LiveServerTestCase.setUpClass()
        cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            LiveServerTestCase.tearDownClass()

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_home_page_when_logged(self):

        self.browser.get('%s%s' % (self.server_url, '/signup'))
        self.assertIn('Signup', self.browser.title)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        verify_password = self.browser.find_element_by_id('verify_password_input')
        email = self.browser.find_element_by_id('email_input')
        username.send_keys('bbbb')
        password.send_keys('bbbb')
        verify_password.send_keys('bbbb')
        email.send_keys('bbbb@mail.com')
        button = self.browser.find_element_by_id('signup_button')
        button.click()
        time.sleep(2)
        self.assertIn('Homepage', self.browser.title)
        self.browser.get('/logout/')
        time.sleep(0.5)
        self.assertIn('Login', self.browser.title)
        self.browser.find_element_by_id('sign_in_url').click()
        self.browser.implicitly_wait(3)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        verify_password = self.browser.find_element_by_id('verify_password_input')
        email = self.browser.find_element_by_id('email_input')
        username.send_keys('aaaa')
        password.send_keys('asdasdasd')
        verify_password.send_keys('asdasdasd')
        email.send_keys('aaaa@mail.com')
        button = self.browser.find_element_by_id('signup_button')
        button.click()
        time.sleep(2)

        self.browser.find_element_by_id('username')
        self.browser.find_element_by_id('dropdown_logout_url')
        friend_search = self.browser.find_element_by_id('search_friends_bar')
        friend_search.send_keys('bbbb')
        search_friend_button = self.browser.find_element_by_id('search_friends_button')
        search_friend_button.click()
        time.sleep(1)
        self.assertIn('Search Results', self.browser.title)
        result = self.browser.find_element_by_link_text('bbbb')
        result.click()
        time.sleep(1)
        self.assertIn('Profile of bbbb', self.browser.title)
        add_friend_button = self.browser.find_element_by_id('add_friend_button')
        add_friend_button.click()
        time.sleep(1)
        self.assertIn('Friend Request Sent', self.browser.find_element_by_class_name("main").get_attribute('innerHTML'))
        self.browser.get('/logout/')
        time.sleep(0.5)
        self.assertIn('Login', self.browser.title)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        username.send_keys('bbbb')
        password.send_keys('bbbb')
        self.assertEqual(username.get_attribute('placeholder'), 'Username')
        self.assertEqual(password.get_attribute('placeholder'), 'Password')
        login = self.browser.find_element_by_id('login_button')
        login.click()
        time.sleep(1)

        self.browser.get('/settings/')
        self.browser.find_element_by_id("friend_requests")
        self.browser.find_element_by_class_name("friend_request_message")
        accept_button = self.browser.find_element_by_xpath("//button[contains(.,'Accept')]")
        accept_button.click()
        time.sleep(1)
        friend_list = self.browser.find_element_by_id('friends_list')
        self.assertIn('aaaa', friend_list.get_attribute('innerHTML'))

        self.browser.get(self.server_url)
        send_post = self.browser.find_element_by_id('send_post')
        send_post.click()
        time.sleep(10)
        self.assertIn('New Post', self.browser.title)
        title = self.browser.find_element_by_id('title_input')
        img = self.browser.find_element_by_id('img_input')
        url = self.browser.find_element_by_id('url_input')
        # rating = self.browser.find_element_by_id('rating_container')
        comment = self.browser.find_element_by_id('comment_textarea')
        self.browser.find_element_by_id('send_to_button')
        send_post = self.browser.find_element_by_id('send_post_button')
        title.send_keys('Ip Man')
        img.send_keys('url to image')
        url.send_keys('http://www.imdb.com/title/tt1220719/')
        self.browser.find_element_by_class_name('glyphicon').click()
        time.sleep(5)
        comment.send_keys('One of the best fighting movies I have ever seen.')
        # send_to.click()
        send_post.click()
        time.sleep(2)
        # Check Settings page. No redirects because I'm still logged in.
        settings = self.browser.find_element_by_id('dropdown_settings_link')
        settings.click()
        time.sleep(2)
        self.assertIn('Settings', self.browser.title)
        self.browser.find_element_by_id('toggle_change_name_form').click()
        self.browser.find_element_by_id('change_name_form')
        change_name = self.browser.find_element_by_id('change_name_input')
        change_name.send_keys('My new cool name')
        submit_change = self.browser.find_element_by_id('submit_change_name_button')
        submit_change.click()
        time.sleep(1)
        self.browser.find_element_by_id('change_password_button').click()
        change_password = self.browser.find_element_by_id('change_password_input')
        change_password.send_keys('mynewcoolpassword')
        verify_change_password = self.browser.find_element_by_id('verify_password_input')
        verify_change_password.send_keys('mynewcoolpassword')
        submit_change = self.browser.find_element_by_id('submit_change_password_button')
        submit_change.click()
        time.sleep(1)
        self.browser.find_element_by_id('name_tag')
        self.browser.find_element_by_id('show_change_avatar_form').click()
        self.browser.find_element_by_id('selected_file_input')
        self.browser.find_element_by_id('change_avatar_button')
        self.browser.find_element_by_id('avatar')
        self.browser.find_element_by_id('friends_list')

        self.browser.get('/login')

        time.sleep(2)

        self.assertIn('Login', self.browser.title)
        self.browser.find_element_by_id('username_input').send_keys('aaaa')
        self.browser.find_element_by_id('password_input').send_keys('asdasdasd')

        self.browser.find_element_by_id('login_button').click()
        time.sleep(4)
        self.assertIn('Ip Man', self.browser.find_element_by_class_name("main").get_attribute("innerHTML"))
        self.browser.get('/settings')
        self.browser.find_element_by_id('show_delete_account_modal').click()
        time.sleep(3)
        self.browser.switch_to.alert
        self.browser.find_element_by_id('delete_account_button').click()
        time.sleep(1)
        self.assertIn('Login', self.browser.title)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
