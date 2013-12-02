from django.test import TestCase
import re
from django.contrib.auth.models import User
from django.core import mail
from django.test import Client
from AuctionApp.models import *
from datetime import datetime, timedelta


class CreateAuctionTest(TestCase):

    def setUp(self):
        User.objects.create_user('Test', 'test@test.com', '1234abcd')
        self.client.login(username='Test', password='1234abcd')

    def test_create_auction(self):

        auction_count_start = Auction.objects.count()
        response = self.client.post(path='/auction/', data={})

        #Check response.status_code
        self.assertEqual(response.status_code, 200)

        auction_count_end = Auction.objects.count()

        #Check that auction was created
        self.assertEqual(auction_count_start + 1, auction_count_end)

    def test_create_auction_publish(self):

        response = self.client.post(path='/auction/', data={},)
        auction = response.context['auction']

#        redirect_chain = response.redirect_chain
#        url = redirect_chain[0]
#        url = url[0]
#        str(url)

#        expression = re.compile(r'(?P<id>\d+)')
#        result = expression.search(url)
#        auction_id = result.group('id')

        starttime = datetime.now()
        tmp = starttime + timedelta(hours=73)
        endtime = datetime.strftime(tmp, '%H:%M %d-%m-%Y')
        version = 0
        title = "Test Title"
        content = "Testing Description"
        min_price = 11.11
        auction_id = auction.id

        #Check that auction becomes active!
        self.client.post(path='/addauction/', data={'endtime': endtime, 'version': version, 'title': title,
                                                    'content': content, 'min_price': min_price,
                                                    'endtime': endtime, 'id': auction_id})

        auction = Auction.objects.get(id=auction_id)
        self.assertEqual(auction.is_active, True)

