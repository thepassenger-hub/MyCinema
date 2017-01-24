from selenium import webdriver
import unittest

class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_login_page_on_first_visit(self):
        self.browser.get('http://localhost:8000')

        self.assertIn('Login', self.browser.title)
        username = self.browser.find_element_by_id('username_input')
        password = self.browser.find_element_by_id('password_input')
        self.assertEqual(username.get_attribute('placeholder'), 'Username')
        self.assertEqual(password.get_attribute('placeholder'), 'Password')
        sign_in = self.browser.find_element_by_id('sign_in_url')

        self.fail("finish the test")


if __name__ == '__main__':
    unittest.main(warnings='ignore')
