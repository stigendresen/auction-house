from datetime import datetime

from django.test import TestCase


class CreateAuctionTest(TestCase):
    def setUp(self):
        User.objects.create_user('Test', 'test@test.com', '1234abcd')
        self.client.login(username='Test', password='1234abcd')

    def create_auction_publish(self):
        start = datetime.now()
        stop = start + timedelta(hours=4)


    def tearDown(self):




