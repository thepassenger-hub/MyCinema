from selenium import webdriver
import django
from django.test import LiveServerTestCase
import unittest
import os
import sys
import time

sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "movieapp_backend.settings")  # or whatever
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
        self.browser.set_window_size(768, 768)
        self.browser.set_window_position(0,0)
        self.browser.implicitly_wait(3)
        self.browser_2 = webdriver.Firefox()
        self.browser_2.set_window_size(768, 768)
        time.sleep(0.5)
        self.browser_2.set_window_position(683, 0)
        self.browser_2.implicitly_wait(3)
        
    def tearDown(self):
        self.browser.quit()
        self.browser_2.quit()        

    def test_home_page_when_logged(self):

        # Opening Signup page and registering new user.
        self.browser.get('%s%s' % (self.server_url, '/signup'))
        self.browser_2.get('%s%s' % (self.server_url, '/signup'))
        time.sleep(5)
        self.assertIn('Signup', self.browser.title)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        verify_password = self.browser.find_element_by_id(
            'verify_password_input')
        email = self.browser.find_element_by_id('email_input')
        username.send_keys('bbbb')
        password.send_keys('bbbb')
        verify_password.send_keys('bbbb')
        email.send_keys('bbbb@mail.com')
        button = self.browser.find_element_by_id('signup_button')
        button.click()
        time.sleep(2)
        #Redirected to HomePage then logout and register friend user
        self.assertIn('Homepage', self.browser.title)
        self.browser.get('/logout/')
        time.sleep(0.5)
        self.assertIn('Login', self.browser.title)
        username = self.browser_2.find_element_by_id('username_input')
        password = self.browser_2.find_element_by_id('password_input')
        verify_password = self.browser_2.find_element_by_id(
            'verify_password_input')
        email = self.browser_2.find_element_by_id('email_input')
        username.send_keys('aaaa')
        password.send_keys('asdasdasd')
        verify_password.send_keys('asdasdasd')
        email.send_keys('aaaa@mail.com')
        button = self.browser_2.find_element_by_id('signup_button')
        button.click()
        time.sleep(2)
        #Search for friend profile
        self.browser_2.find_element_by_id('username')
        self.browser_2.find_element_by_id('dropdown_logout_url')
        friend_search = self.browser_2.find_element_by_id('search_friends_bar')
        friend_search.send_keys('bbbb')
        search_friend_button = self.browser_2.find_element_by_id(
            'search_friends_button')
        search_friend_button.click()
        time.sleep(1)
        self.assertIn('Search Results', self.browser_2.title)
        result = self.browser_2.find_element_by_link_text('bbbb')
        result.click()
        time.sleep(1)
        # Check friend profile and send him friend request.
        self.assertIn('Profile of bbbb', self.browser_2.title)
        add_friend_button = self.browser_2.find_element_by_id(
            'add_friend_button')
        add_friend_button.click()
        time.sleep(1)
        self.assertIn('Friend Request Sent', self.browser_2.find_element_by_class_name(
            "main").get_attribute('innerHTML'))
        # self.browser.get('/logout/')
        time.sleep(0.5)
        # Login as and check settings page 
        # self.assertIn('Login', self.browser.title)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        username.send_keys('bbbb')
        password.send_keys('bbbb')
        self.assertEqual(username.get_attribute('placeholder'), 'Username')
        self.assertEqual(password.get_attribute('placeholder'), 'Password')
        login = self.browser.find_element_by_id('login_button')
        login.click()
        time.sleep(1)
        #Accept friend request
        self.browser.get('/settings/')
        self.browser.find_element_by_id("friend_requests")
        self.browser.find_element_by_class_name("friend_request_message")
        accept_button = self.browser.find_element_by_xpath(
            "//button[contains(.,'Accept')]")
        accept_button.click()
        time.sleep(1)
        friend_list = self.browser.find_element_by_id('friends_list')
        self.assertIn('aaaa', friend_list.get_attribute('innerHTML'))

        self.browser.get(self.server_url)
        # Send Post to friend
        send_post = self.browser.find_element_by_id('send_post')
        send_post.click()
        time.sleep(10)
        self.assertIn('New Post', self.browser.title)
        title = self.browser.find_element_by_id('title_input')
        img = self.browser.find_element_by_id('img_input')
        url = self.browser.find_element_by_id('url_input')
        comment = self.browser.find_element_by_id('comment_textarea')
        self.browser.find_element_by_id('send_to_button')
        send_post = self.browser.find_element_by_id('send_post_button')
        title.send_keys('Ip Man')
        img.send_keys('url to image')
        url.send_keys('http://www.imdb.com/title/tt1220719/')
        self.browser.find_element_by_class_name('glyphicon-star-empty').click()
        # self.browser.execute_script("document.getElementByClass")
        time.sleep(5)
        comment.send_keys('One of the best fighting movies I have ever seen.')
        # send_post.click() # To avoid api usage
        # time.sleep(10)
        # Check Settings page. No redirects because I'm still logged in.
        # Change name, avatar, password and friendlist.
        settings = self.browser.find_element_by_id('dropdown_settings_link')
        settings.click()
        time.sleep(2)
        self.assertIn('Settings', self.browser.title)
        self.browser.find_element_by_id('toggle_change_name_form').click()
        self.browser.find_element_by_id('change_name_form')
        change_name = self.browser.find_element_by_id('change_name_input')
        change_name.send_keys('My new cool name')
        submit_change = self.browser.find_element_by_id(
            'submit_change_name_button')
        submit_change.click()
        time.sleep(1)
        self.browser.find_element_by_id('change_password_button').click()
        change_password = self.browser.find_element_by_id(
            'change_password_input')
        change_password.send_keys('mynewcoolpassword')
        verify_change_password = self.browser.find_element_by_id(
            'verify_password_input')
        verify_change_password.send_keys('mynewcoolpassword')
        submit_change = self.browser.find_element_by_id(
            'submit_change_password_button')
        submit_change.click()
        time.sleep(1)
        self.browser.find_element_by_id('name_tag')
        self.browser.find_element_by_id('show_change_avatar_form').click()
        self.browser.find_element_by_id('selected_file_input')
        self.browser.find_element_by_id('change_avatar_button')
        self.browser.find_element_by_id('avatar')
        self.browser.find_element_by_id('friends_list')

        # self.browser.get('/login')

        time.sleep(2)
        # Check if post was received then delete account
        # self.assertIn('Login', self.browser.title)
        # self.browser.find_element_by_id('username_input').send_keys('aaaa')
        # self.browser.find_element_by_id(
        #     'password_input').send_keys('asdasdasd')

        # self.browser.find_element_by_id('login_button').click()
        self.browser_2.get(self.server_url)
        time.sleep(1)
        # self.assertIn('Ip Man', self.browser_2.find_element_by_class_name(
        #     "main").get_attribute("innerHTML"))
        # Send chat message to friend. 
        chat = self.browser_2.find_element_by_id("open_chat")
        chat.click()
        time.sleep(2)

        friend = self.browser_2.find_element_by_class_name("friends")
        friend.click()
        time.sleep(5)
        message_box = self.browser_2.find_element_by_id("chat_message")
        message_box.send_keys('Cool stuff')
        time.sleep(2)
        send_chat_message = self.browser_2.find_element_by_id("send_chat_message")
        send_chat_message.click()
        # Notification of chat message from user_2
        time.sleep(2)
        self.browser.find_element_by_id('notifications_counter').click()
        time.sleep(2)
        self.browser.find_element_by_class_name('notifications').click()
        time.sleep(2)
        self.assertIn('Cool stuff', self.browser.find_element_by_class_name('open_chat_messages').get_attribute('innerHTML'))
        self.browser.find_element_by_id('chat_message').send_keys('Gotcha')
        self.browser.find_element_by_id("send_chat_message").click()
        time.sleep(2)
        self.browser.find_element_by_id('close_chat_button').click()
        # User 2 should receive message in chat
        self.assertIn('Gotcha', self.browser_2.find_element_by_class_name('open_chat_messages').get_attribute('innerHTML'))
        # Delete user 2 account
        self.browser_2.get('/settings')
        self.browser_2.find_element_by_id('show_delete_account_modal').click()
        time.sleep(3)
        self.browser_2.switch_to.alert
        self.browser_2.find_element_by_id('delete_account_button').click()
        time.sleep(1)
        self.assertIn('Login', self.browser_2.title)

if __name__ == '__main__':
    unittest.main(warnings='ignore')
