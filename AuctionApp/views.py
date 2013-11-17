from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib import messages
from AuctionApp.models import *

def home(request):
    auctions = User.objects.order_by('id')

    if not 'loggedin' in request.session:
        request.session['loggedin'] = 0

    if request.method == "POST":
        return render(request, "register_user.html")

    if request.session['loggedin']:
        messages.warning(request, 'We are logged in')


    return render(request, "index.html", {'auctions': auctions, 'loggedin': request.session['loggedin']})


def reg_user(request):
    #REMEMBER TO PREVENT SQL-INJECTION
    if request.POST["pword"].strip() == request.POST["vpword"]:

        newUser = User.objects.create()
        newUser.address = request.POST["address"].strip()
        newUser.email = request.POST["email"].strip()
        newUser.password = request.POST["pword"].strip()
        newUser.firstname = request.POST["fname"].strip()
        newUser.surname = request.POST["sname"].strip()
        newUser.save()

        messages.success(request, 'New user has been created!')
        return HttpResponseRedirect("/auctionhouse/")

    else:

        messages.error(request, 'Error creating user')
        return HttpResponseRedirect("/auctionhouse/")


def login(request):

    request.session['loggedin'] = 1
    tmpUser = User.objects.get(email=request.POST["email"].strip())

    if tmpUser.checkPassword(request.POST["pword"].strip()):
        messages.success(request, 'LOGGED IN SUCCESSFULLY')

    return HttpResponseRedirect("/auctionhouse/")


def logout(request):

    if request.method == "POST" and request.session['loggedin'] == True:
        request.session['loggedin'] = False
        request.session.flush()
        

    return HttpResponseRedirect("/auctionhouse/")