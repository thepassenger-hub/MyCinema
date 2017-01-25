from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.db import IntegrityError  # create_user postgres custom exception

from utils.regex_matching import are_params_invalid

@login_required()
def home_page(request):

    return render(request, 'movieapp_frontend/index.html')


def login(request):
    return render(request, 'movieapp_frontend/login.html')

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
            User.objects.create_user(username=username,
                                            email=email,
                                            password=password)
        except IntegrityError:
            error = "Username already exists"
            return render(request, 'movieapp_frontend/signup.html',
                          {'error': error})
        except:
            error = "There was an error. Try again later."
            return render(request, 'movieapp_frontend/signup.html',
                          {'error': error})
        return redirect(home_page)
