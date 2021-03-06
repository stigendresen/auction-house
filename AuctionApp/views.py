from datetime import datetime, timedelta
import re

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.utils.timezone import utc
from AuctionApp.models import *


def home(request):
    if request.method == "POST":

        if request.POST.get('login', ''):
            log_in(request)

        elif request.POST.get('', 'reguser'):
            return render(request, "register_user.html")

    if request.user.is_superuser:
        auctions = Auction.objects.order_by('starttime')
    else:
        auctions = Auction.objects.filter(is_active=True)

    if request.method == "GET":

        if request.GET.get('searchbutton'):
            searchvalue = request.GET['searchfield']

            if not searchvalue == "":
                auctions = Auction.objects.filter(title=searchvalue)

    if not 'loggedin' in request.session:
        request.session['loggedin'] = 0

    return render(request, "index.html", {'auctions': auctions, 'loggedin': request.session['loggedin'],
                                          'user': request.user})


def reg_user(request):
    #REMEMBER TO PREVENT SQL-INJECTION
    if request.POST["pword"].strip() == request.POST["vpword"]:

        username = request.POST["uname"]

        if len(User.objects.filter(username=username)) > 0:
            return HttpResponse("Username already exists")

        email = request.POST["email"]
        password = request.POST["pword"].strip()

        if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            email = request.POST["email"].strip()

            if len(password) < 5:
                return HttpResponse("Password needs to be at least 4 characters long")

        else:
            return HttpResponse("Invalid email-address")

        firstname = request.POST["fname"].strip()
        surname = request.POST["sname"].strip()

        tmpUser = User.objects.create_user(username, email, password)
        tmpUser.last_name = surname
        tmpUser.first_name = firstname
        tmpUser.save()

        messages.success(request, 'New user has been created!')
        return HttpResponseRedirect("/auctionhouse/")

    else:

        messages.error(request, 'Error creating user')
        return HttpResponseRedirect("/auctionhouse/")


def log_in(request):
    if not request.method == "POST":
        return HttpResponse("Error logging in")

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


@login_required(login_url="/auctionhouse/")
def get_user(request):
    tmp_user = request.user
    request.session.set_expiry(1800)
    auctions = Auction.objects.filter(ownerid=tmp_user)
    return render(request, "user_profile.html", {'user': tmp_user, 'auctions': auctions})


@login_required(login_url="/auctionhouse/")
def add_auction(request):
    if request.method == "POST":

        edited_version = int(request.POST["version"])
        auction = Auction.objects.get(id=request.POST["id"])

        if auction.is_locked:
            return HttpResponse("Auction is banned")

        if len(request.POST["title"]) < 5:
            return HttpResponse("Title is too short")

        if not auction.is_active:
            auction.title = request.POST["title"]
            auction.min_price = float(request.POST["min_price"])
            endtime = request.POST["endtime"]
            auction.content = request.POST["content"]

            tmp_time = datetime.strptime(endtime, '%H:%M %d-%m-%Y')

            if datetime.utcnow() > (tmp_time - timedelta(hours=72)):
                return HttpResponse("The end-time is invalid")

            tmp_time = tmp_time.replace(tzinfo=utc)
            auction.endtime = tmp_time

            try:
                auction.is_active = True
                auction.save()

            except:
                return HttpResponse("ERROR!: Could not publish auction, \nCheck values!")

        elif auction.is_active and auction.version == edited_version:

            auction.content = request.POST["content"]
            auction.title = request.POST["title"]
            auction.version = auction.version + 1

            try:
                auction.save()

            except:
                return HttpResponse("ERROR!: Could not publish auction, \nCheck values!")

        else:
            # the description has changed. Let the user resolve the conflict
            return render_to_response("edit_auction_error.html",
                                      {'auction': auction}, context_instance=RequestContext(request))

        messages.success(request, 'Auction Published')
        return HttpResponseRedirect("/userprofile/")


@login_required(login_url="/show_auction/")
def place_bid(request, auction):

    if request.user == auction.ownerid or auction.latest_bid_by == request.user:
        return None

    bid_amount = request.POST['bidfield']

    try:
        new_bid = float(bid_amount)

        if new_bid > auction.min_price:
            auction.min_price = new_bid
            auction.latest_bid_by = request.user
            auction.save()

        else:
            return HttpResponse("Couldn't bid. Amount is too low")

    except:
        messages.error(request, 'Enter a valid number')


def show_auction(request, auction_id):

    try:
        auction = Auction.objects.get(id=auction_id)

        if request.method == "POST" and auction.is_active:
            place_bid(request, auction)

    except:
        messages.error(request, 'An error has occured.')
        return HttpResponse('Could not display auction')

    return render(request, "show_auction.html", {'auction': auction, 'user': request.user})


@login_required(login_url="/auctionhouse/")
def create_auction(request):
    auction = Auction.objects.create(ownerid=request.user, latest_bid_by=request.user)
    tmp_endtime = calculate_endtime()

    #tmp_str = '/auction/' + str(auction.id)
    #return HttpResponseRedirect(tmp_str)

    return render_to_response("edit_auction.html",
                            {'auction': auction, 'possible_endtime': tmp_endtime,
                            }, context_instance=RequestContext(request))


def calculate_endtime():

    return datetime.now() + timedelta(hours=72)


@login_required(login_url="/auctionhouse/")
def edit_auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)

    if auction.ownerid == request.user:
        auction = Auction.objects.get(id=auction_id)
        tmp_endtime = calculate_endtime()

        return render_to_response("edit_auction.html",
                                  {'auction': auction, 'possible_endtime': tmp_endtime
                                  }, context_instance=RequestContext(request))


@login_required(login_url="/auctionhouse/")
def delete_auction(request, auction_id):
    if request.method == "POST" and request.user.is_superuser:

        try:
            auction = Auction.objects.get(id=auction_id)
            auction.delete()
            messages.success(request, "Auction deleted!")

        except:
            return HttpResponse('Auction does not exist')

        return HttpResponseRedirect("/auctionhouse/")


def set_language(request):

    if request.method == "POST":
        if 'no' == request.POST.get("NO"):
            lang = 'no'
        elif 'fi' == request.POST.get('FI'):
            lang = 'fi'
        elif 'sv' == request.POST.get('SV'):
            lang = 'sv'
        elif 'dk' == request.POST.get('DK'):
            lang = 'dk'
        else:
            lang = 'en'

        if request.user.is_authenticated():

            language = Language(user=request.user, language=lang)
            language.save()
            request.session['django_language'] = language.language

            return HttpResponseRedirect('/auctionhouse/')

        else:

            request.session['django_language'] = lang
            return HttpResponseRedirect('/auctionhouse/')


def get_current_url(request):
    return render_to_response('/', {}, context_instance=RequestContext(request))


def ban_auction(request, auction_id):
    if request.method == "POST" and request.POST.get('ban_auction', ''):
        try:
            auction = Auction.objects.get(id=auction_id)
            auction.is_locked = True
            auction.latest_bid_by = auction.ownerid
            auction.ownerid = request.user
            auction.min_price = 0
            auction.is_active = False
            auction.save()
            messages.success(request, 'Auction is banned')

        except:
            messages.error(request, 'Could not ban auction')

    elif request.method == "POST" and request.POST.get('', 'unban_auction'):
        try:
            auction = Auction.objects.get(id=auction_id)
            auction.is_locked = False
            auction.ownerid = auction.latest_bid_by
            auction.save()
            messages.success(request, 'Auction is re-submittable')

        except:
            messages.error(request, 'Could not UNBAN auction')

    return HttpResponseRedirect('/auctionhouse/')


def edit_user(request):

    user = request.user
    if request.method == "GET" and request.user.is_authenticated():
        return render(request, "edit_user.html", {'user':user})

    elif request.method == "POST" and request.user.is_authenticated():
        username = user.username
        user = authenticate(username=username, password=request.POST['pword'])

        if request.POST['pword'] == request.POST['vpword'] and user is not None and request.POST['pword'] > 5:

            email = request.POST['email']
            if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):

                request.user.set_password(request.POST['pword'])
                request.user.email = email
                request.user.save()

                messages.success(request, 'Userinformation changed')
                return HttpResponseRedirect('/userprofile/')

            else:
                return HttpResponse("Something went wrong, check Email")

        else:
            return HttpResponse("Check the password")

    else:
        return HttpResponseRedirect('/auctionhouse/')
