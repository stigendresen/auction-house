from django.conf.urls import patterns, include, url
from django.contrib import admin

from AuctionApp.views import *


admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'Auction.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       (r'^auctionhouse/$', home),
                       (r'^registeruser/$', reg_user),
                       (r'^logout/$', log_out),
                       (r'^userprofile', get_user),
                       (r'^auction/$', create_auction),
                       (r'^auction/(?P<auction_id>\d+)', show_auction),
                       (r'^addauction/$', add_auction),
                       (r'^editauction/(?P<auction_id>\d+)/$', edit_auction),
                       (r'^deleteauction/(?P<auction_id>\d+)/$', delete_auction),
                       (r'^banauction/(?P<auction_id>\d+)/$', ban_auction),

                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
