from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone


class Auction(models.Model):

    id = models.AutoField(primary_key=True)
    ownerid = models.ForeignKey(User, related_name="created")
    starttime = models.DateTimeField(default=datetime.utcnow(), blank=True)
    endtime = models.DateTimeField(default=timezone.now(), blank=True)
    title = models.CharField(max_length=30, default="New Auction")
    content = models.TextField()
    version = models.PositiveIntegerField(default=0)
    min_price = models.FloatField(default=0.00)
    is_active = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    latest_bid_by = models.ForeignKey(User, related_name="bids")


class Language(models.Model):

    user = models.ForeignKey(User, primary_key=True)
    language = models.CharField(max_length=15, default='en')

    @classmethod
    def get_language_by_user(cls, user):
        try:
            return cls.objects.get(user=user)

        except:
            return None


'''
class Bid(models.Model):

    auction = models.ForeignKey(Auction)
    bidder = models.ForeignKey(User)
    amount = models.FloatField(default=0.00)
    timestamp = models.DateTimeField()
'''

