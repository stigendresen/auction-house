from django.db import models
from datetime import datetime


class User (models.Model):

    id = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=255)
    firstname = models.CharField(max_length=15)
    surname = models.CharField(max_length=20)
    address = models.TextField()
    password = models.CharField(max_length=30)
    #md5pass = models.b64encode(p, altchars=None)
    phone = models.CharField(max_length=15)

    @classmethod
    def checkPassword (cls, auction_password):
        return len(cls.objects.filter(password = auction_password)) > 0


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
