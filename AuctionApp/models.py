from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Auction (models.Model):

    id = models.AutoField(primary_key=True)
    ownerid = models.ForeignKey(User)
    starttime = models.DateTimeField(default=datetime.now(), blank=True)
    endtime = models.DateTimeField(default=datetime.now(), blank=True)
    title = models.CharField(max_length=30)
    content = models.TextField()
    version = models.IntegerField(default=0)
    minprice = models.FloatField(default=0.00)

    @classmethod
    def getById (cls, auction_id):
        return cls.objects.get(id = auction_id)
