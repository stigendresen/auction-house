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
from django.core.urlresolvers import reverse


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

    tmp_user = request.user
    auctions = Auction.objects.filter(ownerid=tmp_user)
    return render(request, "user_profile.html", {'user': tmp_user, 'auctions': auctions})


@login_required(login_url="/auctionhouse/")
def add_auction(request):

    auction = Auction.objects.get(ownerid=request.user)
    auction.title = request.POST["title"]
    auction.content = request.POST["description"]
    auction.minprice = request.POST["min_price"]
    auction.save()


def show_auction(request, auction_id):

    auction = Auction.objects.get(id=auction_id)
    return render(request, "show_auction.html", {'auction': auction, 'user': request.user})


def create_auction(request):

    auction = Auction.objects.create(ownerid=request.user)
    tmp_str = '/auction/' + str(auction.id)

    return HttpResponseRedirect(tmp_str)


def edit_auction(request, auction_id):

    auction = Auction.objects.get(id=auction_id)

    return render_to_response("edit_auction.html",
                              {'auction': auction}, context_instance=RequestContext(request))


@login_required(login_url="/auctionhouse/")
def delete_auction(request, auction_id):

    if request.method == "POST":

        try:
            auction = Auction.objects.get(id=auction_id)
            auction.delete()
            messages.success(request, "Auction deleted!")

        except:
            return HttpResponse('Auction does not exist')

        return HttpResponseRedirect("/userprofile/")

    return