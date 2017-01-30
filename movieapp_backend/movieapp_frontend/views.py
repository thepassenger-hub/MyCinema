from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError  # create_user postgres custom exception

from movie_app.models import MoviePost, Profile, Friendship
from utils.regex_matching import are_params_invalid, are_fields_invalid
from .forms import ChangeNameForm, ChangePasswordForm
import re

PASSWORD_REGEX = re.compile(r'^.{3,20}$')

@login_required()
def home_page(request):
    return render(request, 'movieapp_frontend/index.html')

@login_required()
def new_post_page(request):
    if request.method == 'GET':
        return render(request, 'movieapp_frontend/newpost.html')
    if request.method == 'POST':
        title = request.POST.get('title')
        image_url = request.POST.get('image_url')
        rating = request.POST.get('rating')
        content = request.POST.get('content')
        send_to = request.POST.get('send_to')
        user = request.user

        error = are_fields_invalid(title, rating)
        if error:
            return render(request, 'movieapp_frontend/newpost.html', {'error': error})


        movie_post = MoviePost()
        movie_post.title = title
        movie_post.rating = int(rating)
        movie_post.image_url = image_url
        movie_post.content = content
        movie_post.user = user
        movie_post.save()

        friends_of_user = user.profile.get_friends()

        if send_to:
            send_to = send_to.split(',')
            for username in send_to:
                try:
                    out = User.objects.get(username=username)
                    if out in friends_of_user:
                        movie_post.send_to.add(out)
                except:
                    pass
        else:
            for friend in friends_of_user:
                try:
                    movie_post.send_to.add(friend)
                except:
                    pass

        return render(request, 'movieapp_frontend/newpost.html', {'success': 'Post Sent'})



def login_page(request):
    if request.method == 'GET':
        return render(request, 'movieapp_frontend/login.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username:
            error = 'Invalid Username'
            return render(request, 'movieapp_frontend/login.html', {'error': error})
        if not password:
            error = 'Invalid Password'
            return render(request, 'movieapp_frontend/login.html', {'error': error})

        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            error = "Username doesn't exist"
            return render(request, 'movieapp_frontend/login.html', {'error': error})

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect(home_page)
        else:
            error = 'Wrong Password. Try again'
            return render(request, 'movieapp_frontend/login.html', {'error': error})

def logout_page(request):
    logout(request)
    return redirect(home_page)

def signup(request):
    if request.method == 'GET':
        return render(request, 'movieapp_frontend/signup.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        verify_password = request.POST.get('verify_password')
        email = request.POST.get('email')
        if are_params_invalid(username, password, email):
            error = are_params_invalid(username, password, email)
            return render(request, 'movieapp_frontend/signup.html',
                          {'error': error})
        if password != verify_password:
            error = "Passwords don't match"
            return render(request, 'movieapp_frontend/signup.html',
                          {'error': error})

        try:
            create_user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password)
            Profile(user=create_user).save()
        except IntegrityError:
            error = "Username already exists"
            return render(request, 'movieapp_frontend/signup.html',
                          {'error': error})
        except:
            error = "There was an error. Try again later."
            return render(request, 'movieapp_frontend/signup.html',
                          {'error': error})

        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect(home_page)

@login_required()
def settings_page(request):
    if request.method == 'GET':
        change_name_form = ChangeNameForm()
        change_password_form = ChangePasswordForm()
        return render(request, 'movieapp_frontend/settings.html', {'change_name_form': change_name_form,
                                                                   'change_password_form': change_password_form})
    # if request.method == 'POST':
        # new_name_form = ChangeNameForm(request.POST)
        # if new_name_form.is_valid():
        # if new_name != None:
        #     if new_name.strip() == '':
        #         error = 'Invalid name'
        #         return render(request, 'movieapp_frontend/settings.html', {'error': error})
        #     profile = request.user.profile
        #     profile.name = new_name
        #     profile.save()
        #     return redirect(settings_page)

        # new_password = request.POST.get('new_password')
        # verify_new_password = request.POST.get('verify_new_password')
        # if new_password or verify_new_password:
        #     error = are_passwords_invalid(new_password, verify_new_password)
        #     if error:
        #         return render(request, 'movieapp_frontend/settings.html', {'error': error})
        #     request.user.set_password(new_password)
        #     request.user.save()
        #     update_session_auth_hash(request, request.user)
        #     return redirect(settings_page)

@login_required()
def change_name(request):
    if request.method == 'POST':
        new_name_form = ChangeNameForm(request.POST, instance=request.user.profile)
        if new_name_form.is_valid():
            new_name_form.save()
            return redirect(settings_page)

@login_required()
def change_password(request):
    if request.method == 'POST':
        change_password_form = ChangePasswordForm(request.POST)
        if change_password_form.is_valid():
            request.user.set_password(request.POST['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.add_message(request, messages.SUCCESS, 'Password change successful')
        else:
            # Print error message
            for error in change_password_form.errors:
                messages.add_message(request, messages.ERROR, change_password_form.errors[error] )
        return redirect(settings_page)