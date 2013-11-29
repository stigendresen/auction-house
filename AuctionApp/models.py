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
    version = models.IntegerField(default=0)
    min_price = models.FloatField(default=0.00)
    is_active = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    latest_bid_by = models.ForeignKey(User, related_name="bids")

    @classmethod
    def getById(cls, auction_id):
        return cls.objects.get(id=auction_id)
