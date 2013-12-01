from unittest import TestCase
from django.contrib.auth.models import User
#from django.core import mail
#from django.test import Client
#from AuctionApp.models import *
from datetime import datetime

class CreateAuctionTest(TestCase):

    def setUp(self):
        User.objects.create_user('Test', 'test@test.com', '1234abcd')
        self.client.login(username='Test', password='1234abcd')

    '''
    def create_auction_publish(self):
        auction_count_start = Auction.objects.count()
        starttime = datetime.now()
        endtime = start + timedelta(hours=73)

        message = self.client.post(self, path='/auction/')


    '''