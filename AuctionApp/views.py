from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib import messages
from AuctionApp.models import *
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate


def home(request):
    auctions = User.objects.order_by('id')

    if not 'loggedin' in request.session:
        request.session['loggedin'] = 0

    if request.method == "POST":
        return render(request, "register_user.html")

    return render(request, "index.html", {'auctions': auctions, 'loggedin': request.session['loggedin']})


def reg_user(request):
    #REMEMBER TO PREVENT SQL-INJECTION
    if request.POST["pword"].strip() == request.POST["vpword"]:

        email = request.POST["email"].strip()
        password = request.POST["pword"].strip()
        firstname = request.POST["fname"].strip()
        surname = request.POST["sname"].strip()

        tmpUser = User.objects.create_user(email, email, password)
        tmpUser.last_name = surname
        tmpUser.first_name = firstname
        tmpUser.save()

        messages.success(request, 'New user has been created!')
        return HttpResponseRedirect("/auctionhouse/")

    else:

        messages.error(request, 'Error creating user')
        return HttpResponseRedirect("/auctionhouse/")


def log_in(request):

    username = request.POST["email"]
    password = request.POST["pword"]
    user = authenticate(username=username, password=password)

    if user is not None:
        if user.is_active:
            login(request, user)
            request.session['loggedin'] = True
            messages.success(request, 'LOGGED IN SUCCESSFULLY')
        else:
            messages.error(request, 'FAILED TO LOG IN')

    else:
        messages.error(request, 'Invalid password or Username')

    return HttpResponseRedirect("/auctionhouse/")


def log_out(request):

    logout(request)
    messages.success(request, 'Successfully logged out!')
    return HttpResponseRedirect("/auctionhouse/")


def get_user(request):

    tmpUser = User.objects.get(email=request.POST["email"].strip())
    return render(request, "user_profile.html", {'user': tmpUser})
