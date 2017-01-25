import re

USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
PASSWORD_REGEX = re.compile(r'^.{3,20}$')
EMAIL_REGEX = re.compile(r'^[\S]+@[\S]+.[\S]+$')

def are_params_invalid(username,password, email):
    if not USERNAME_REGEX.match(username):
        return('Invalid Username')
    if not PASSWORD_REGEX.match(password):
        return('Invalid Password')
    if not EMAIL_REGEX.match(email):
        return('Invalid Email')