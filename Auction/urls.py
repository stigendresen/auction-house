from django.conf.urls import patterns, include, url
from AuctionApp.views import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Auction.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),


    (r'^auctionhouse/$', home),
    (r'^registeruser/$', reg_user),
    (r'^login/$', login),
    (r'^logout/$', logout),
    #(r'^auction/(?P<name>\d+)/$', show_auction),
    #(r'^addauction/$', add_auction),
    #(r'^editauction/$', edit_auction),
    #(r'^deleteauction/(?P<name>\d+)/$', delete_auction),

    url(r'^admin/', include(admin.site.urls)),
)
