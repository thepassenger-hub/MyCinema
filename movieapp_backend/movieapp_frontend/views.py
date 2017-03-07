from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError  # create_user postgres custom exception
from django.http import JsonResponse, HttpResponse

from movie_app.models import MoviePost, Profile, FriendshipRequest, ChatMessage
from utils.scraper import get_image, get_link
from utils.regex_matching import are_params_invalid, are_fields_invalid
from utils.utils import get_friendship
from .forms import ChangeNameForm, ChangePasswordForm, ChangeAvatarForm
import re

PASSWORD_REGEX = re.compile(r'^.{3,20}$')


@login_required()
def home_page(request):
    if request.method == 'GET':
        my_movies = request.user.received_posts.all().order_by('-created')
        return render(request, 'movieapp_frontend/index.html', {'my_movies': my_movies})


@login_required()
def new_post_page(request):
    if request.method == 'GET':
        friends = request.user.profile.get_friends()
        return render(request, 'movieapp_frontend/newpost.html', {'friends': friends, })
    if request.method == 'POST':
        title = request.POST.get('title')
        image_url = request.POST.get('img')
        rating = request.POST.get('rating')
        content = request.POST.get('comment')
        send_to = request.POST.get('send_to')
        url = request.POST.get('url')
        user = request.user

        error = are_fields_invalid(title, rating)
        if error:
            return render(request, 'movieapp_frontend/newpost.html', {'error': error})

        friends_of_user = user.profile.get_friends()
        if not friends_of_user:
            error = 'You must add some friends first.'
            return render(request, 'movieapp_frontend/newpost.html', {'error': error})

        movie_post = MoviePost()
        movie_post.title = title
        movie_post.rating = int(rating)
        if image_url.strip() == '':
            image_url = get_image(title)
        movie_post.image_url = image_url
        movie_post.content = content
        movie_post.user = user
        if url.strip() == '':
            url = get_link(title)
        movie_post.url = url
        movie_post.save()

        # Choose which friends will receive the post.
        # In not specified all friends will receive it.

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
        change_avatar_form = ChangeAvatarForm(use_required_attribute=False)
        user_avatar = request.user.profile.avatar
        # Show only the friend requests not rejected
        friend_requests = request.user.friendship_requests_received.filter(rejected__isnull=True)
        friends_list = request.user.profile.get_friends()
        return render(request, 'movieapp_frontend/settings.html', {'change_name_form': change_name_form,
                                                                   'change_password_form': change_password_form,
                                                                   'change_avatar_form': change_avatar_form,
                                                                   'user_avatar': user_avatar,
                                                                   'friend_requests': friend_requests,
                                                                   'friends_list': friends_list})


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
            request.user.set_password(change_password_form.cleaned_data.get('new_password'))
            request.user.save()
            # Update auth hash so user is still logged in
            update_session_auth_hash(request, request.user)
            messages.add_message(request, messages.SUCCESS, 'Password change successful')
        else:
            # Print error message
            for errors in change_password_form.errors:
                for error in change_password_form.errors[errors]:
                    messages.add_message(request, messages.ERROR, error)
        return redirect(settings_page)


@login_required()
def change_avatar(request):
    if request.method == 'POST':
        change_avatar_form = ChangeAvatarForm(request.POST, request.FILES, instance=request.user.profile)
        if change_avatar_form.is_valid():
            change_avatar_form.save()
            messages.add_message(request, messages.SUCCESS, 'Avatar change successful')
        else:
            for error in change_avatar_form.errors['avatar']:
                messages.add_message(request, messages.ERROR, error)
        return redirect(settings_page)


@login_required()
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        return redirect(home_page)


@login_required()
def search_friends_page(request):
    if request.method == 'GET':
        user_id = request.GET.get('username')
        search_results = None
        if user_id:
            search_results = User.objects.filter(username__icontains=user_id)
        return render(request, 'movieapp_frontend/search_friends.html', {
            'search_results': search_results,
        })


@login_required()
def profile_page(request, user_id):
    if request.method == 'GET':
        profile_user = get_object_or_404(User, username=user_id)
        profile_movies = profile_user.received_posts.all().order_by("-created")
        is_friend = profile_user.profile.is_friend(request.user)
        return render(request, 'movieapp_frontend/profile.html', {
            'profile_user': profile_user,
            'profile_movies': profile_movies,
            'is_friend': is_friend,
        })


@login_required()
def add_friend(request, friend_user_id):
    if request.method == 'POST':
        friend_user = get_object_or_404(User, username=friend_user_id)
        # They can't add themselves as friend
        if friend_user == request.user:
            messages.add_message(request, messages.ERROR, "You can't add yourself.")
            return redirect(profile_page, user_id=friend_user_id)
        # They must not be friends already
        if request.user in friend_user.profile.get_friends():
            messages.add_message(request, messages.ERROR, 'You are already friends.')
            return redirect(profile_page, user_id=friend_user_id)

        # There must be no request from the two users already
        already_sent = FriendshipRequest.objects.filter(Q(from_user=request.user) & Q(to_user=friend_user))
        already_received = FriendshipRequest.objects.filter(Q(from_user=friend_user) & Q(to_user=request.user))
        if already_sent or already_received:
            messages.add_message(request, messages.ERROR, 'A friend request is already pending.')
            return redirect(profile_page, user_id=friend_user_id)

        friendship_request = FriendshipRequest()
        friendship_request.from_user = request.user
        friendship_request.to_user = friend_user
        friendship_request.save()
        messages.add_message(request, messages.SUCCESS, 'Friend Request Sent')
        return redirect(profile_page, user_id=friend_user_id)


@login_required()
def accept_friendship(request, friend_request_id):
    if request.method == 'POST':
        friendship_request = get_object_or_404(FriendshipRequest, pk=friend_request_id)
        friendship_request.accept()
        messages.add_message(request, messages.SUCCESS, 'Friendship Accepted')
        return redirect(settings_page)


@login_required()
def reject_friendship(request, friend_request_id):
    if request.method == 'POST':
        friendship_request = get_object_or_404(FriendshipRequest, pk=friend_request_id)
        friendship_request.reject()
        messages.add_message(request, messages.SUCCESS, 'Friendship Rejected')
        return redirect(settings_page)

@login_required()
def delete_friend(request, friend_user_id):
    if request.method == 'POST':
        friend = get_object_or_404(User, username=friend_user_id)
        if friend in request.user.profile.get_friends():
            friendship = get_friendship(request.user, friend)
            friendship.delete()
            messages.add_message(request, messages.SUCCESS, '%s is not your friend anymore.' % (friend))
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.add_message(request, messages.ERROR, 'You and %s are not friends.' % (friend))
            return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required()
def notifications(request):
    if request.method == 'GET':
        notifications = request.user.profile.get_not_viewed_messages()
        out = list(notifications.values('creator__username'))
        return JsonResponse(out, safe=False)

@login_required()
def chat(request, friend_user_id):
    friend = get_object_or_404(User, username=friend_user_id)
    if request.method == 'GET':
        if friend in request.user.profile.get_friends():
            chat_messages = request.user.profile.get_chat_messages(friend)
            for message in (x for x in chat_messages if x.receiver == request.user and x.viewed == False):
                # if not message.viewed:
                message.viewed = True
                message.save()
            out = list(chat_messages.values('creator__username', 'created', 'message'))
            return JsonResponse(out, safe=False)

    if request.method == 'POST':
        if friend in request.user.profile.get_friends():
            message = request.POST.get('message')
            if message and message.strip():
                new_message = ChatMessage()
                new_message.creator = request.user
                new_message.receiver = friend
                new_message.message = message
                new_message.save()
                return HttpResponse(status=201)





