from __future__ import unicode_literals
from datetime import timedelta
from django.conf import settings
from django.contrib.gis.db import models
#from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from model_utils import Choices
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from encrypted_model_fields.fields import EncryptedCharField
from datetime import datetime
from django.contrib.auth.models import Group

today = datetime.now()
today_path = today.strftime("%Y/%m/%d/%H")

class MonitorJobLog(models.Model):
    job = models.CharField(max_length=255, default='', null=True, blank=True)
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True, blank=True)

class ResponsibleGroup(models.Model):
    group_name = models.CharField(max_length=250)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name        

class Monitor(models.Model):
    MON_TYPE = Choices(
             (1, 'webconnect', ('Web Page')),
             (2, 'ping', ('Ping')), # work in progress
             (3, 'portopen',('Port Open')), # work in progress
             (5, 'ssl_valid', ('SSL Valid')),  # work in progress
             (6, 'latency', ('Network Latency')),  # work in progress
             (7, 'packet_loss', ('Packet Loss')),  # work in progress
    )
    CHECK_OPERATOR = Choices(
             (1, 'postive', ('Positive Integer')),  # work in progress
             (2, 'negative', ('Negative Integer'))  # work in progress
    )

    # name for every check type
    check_name = models.CharField(max_length=50)
    mon_type = models.IntegerField(choices=MON_TYPE, null=True, blank=True, default=MON_TYPE.webconnect)
    check_operator = models.IntegerField(choices=CHECK_OPERATOR, null=True, blank=True, default=CHECK_OPERATOR.postive)
    system_id = models.CharField(max_length=50, default='',null=True, blank=True)
    group_responsible = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)     

    # web connect (string key word checks)
    url = models.CharField(max_length=255, default='', null=True, blank=True)
    string_check = models.CharField(max_length=50, null=True, blank=True)

    # port
    host = models.CharField(max_length=255, default='', null=True, blank=True)
    port = models.CharField(max_length=5, default=0, null=True, blank=True)

    # ssl ignore for host or url
    ignore_ssl_verification = models.BooleanField(default=False)

    #response
    raw_response=models.TextField(null=True,blank=True)
    json_response=models.TextField(null=True,blank=True)


    # Status
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.check_name

class MonitorHistory(models.Model):

    STATUS = Choices(
             (0, 'unknown', ('Unknown')),
             (1, 'down', ('Down')),
             (2, 'warn', ('Warn')),
             (3, 'up', ('UP'))
    )

    monitor = models.ForeignKey(Monitor, null=True, blank=True, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS, null=True, blank=True, default=STATUS.down)
    response = models.TextField(null=True,blank=True)
    response_raw = models.TextField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

class MonitorGroup(models.Model):
    monitor = models.ForeignKey(Monitor, null=True, blank=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group.name    
    


