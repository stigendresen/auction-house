from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib import messages
from AuctionApp.models import *
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils.timezone import utc
import re


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

        auction = Auction.objects.get(id=request.POST["id"])

        if auction.is_locked:
            return render_to_response("AUCTION IS BANNED")

        if len(request.POST["title"]) < 5:
            return HttpResponse("Title is too short")

        if auction.is_active:
            auction.content = request.POST["content"]

        elif not auction.is_active:
            auction.latest_bid_by = request.user
            auction.title = request.POST["title"]
            auction.min_price = request.POST["min_price"]
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

        messages.success(request, 'Auction Published')
        return HttpResponseRedirect("/userprofile/")


@login_required(login_url="/show_auction/")
def place_bid(request, auction):

    if auction.latest_bid_by == auction.ownerid or auction.latest_bid_by == request.user:
        return

    bid_amount = request.POST['bidfield']

    try:
        new_bid = float(bid_amount)

        if new_bid > auction.min_price:

            auction.min_price = new_bid
            auction.latest_bid_by = request.user
            auction.save()

    except:
        messages.error(request, 'Enter a valid number')


def show_auction(request, auction_id):

    try:
        auction = Auction.objects.get(id=auction_id)

        if request.method == "POST" and auction.is_active:
            place_bid(request, auction)

    except:
        messages.error(request, 'Unable to bid')

    return render(request, "show_auction.html", {'auction': auction, 'user': request.user})


@login_required(login_url="/auctionhouse/")
def create_auction(request):
    auction = Auction.objects.create(ownerid=request.user, latest_bid_by=request.user)
    tmp_str = '/auction/' + str(auction.id)

    return HttpResponseRedirect(tmp_str)


@login_required(login_url="/auctionhouse/")
def edit_auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    tmp_endtime = datetime.now() + timedelta(hours=72)

    return render_to_response("edit_auction.html",
                              {'auction': auction, 'possible_endtime': tmp_endtime
                              }, context_instance=RequestContext(request))


@login_required(login_url="/auctionhouse/")
def delete_auction(request, auction_id):
    if request.method == "POST":

        try:
            auction = Auction.objects.get(id=auction_id)
            auction.delete()
            messages.success(request, "Auction deleted!")

        except:
            return HttpResponse('Auction does not exist')

        return HttpResponseRedirect("/auctionhouse/")


def get_current_url(request):
    return render_to_response('/', {}, context_instance=RequestContext(request))
