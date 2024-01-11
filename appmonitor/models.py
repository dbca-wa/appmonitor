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
from django.utils.crypto import get_random_string
from django.db.models import Sum


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

class ResponsibleGroupAdvisoryEmail(models.Model):
    responsible_group = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.CharField(max_length=255, default='', null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return self.email 
    

class ResponsibleGroupOutstandingAdvisoryEmail(models.Model):
    responsible_group = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.CharField(max_length=255, default='', null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return self.email     

class AccessGroup(models.Model):
    
    ACCESS_TYPE = Choices(
             (1, 'view_access', ('View Monitoring Status')),
             (2, 'edit_access', ('Create and Edit Access Platforms')), 
             (3, 'view_access_platform_status', ('View Access Platform Status')),
             (4, 'view_access_package_status', ('View Access Package Status')),

    )

    access_type = models.IntegerField(choices=ACCESS_TYPE, null=True, blank=True, default=None)
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
             (8, 'json_key', ('URL (JSON Key)')),
             (9, 'http_status_code', ('HTTP Status Code'))
    )
    CHECK_OPERATOR = Choices(
             (1, 'postive', ('Positive Integer')),  # work in progress
             (2, 'negative', ('Negative Integer')),  # work in progress
             (3, 'equal_int', ('Equal Integer')),
             (4, 'equal_string', ('Equal String'))
    )

    # name for every check type
    check_name = models.CharField(max_length=50)
    mon_type = models.IntegerField(choices=MON_TYPE, null=True, blank=True, default=MON_TYPE.webconnect)
    check_operator = models.IntegerField(choices=CHECK_OPERATOR, null=True, blank=True, default=CHECK_OPERATOR.postive)
    system_id = models.CharField(max_length=50, default='',null=True, blank=True)
    group_responsible = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)     
    use_auth2_token = models.BooleanField(default=False)

    # web connect (string key word checks)
    url = models.CharField(max_length=255, default='', null=True, blank=True)
    string_check = models.CharField(max_length=50, null=True, blank=True)
    json_key = models.CharField(max_length=400, null=True, blank=True)
    status_code = models.IntegerField(default=200, null=True, blank=True)

    # port
    host = models.CharField(max_length=255, default='', null=True, blank=True)
    port = models.CharField(max_length=5, default=0, null=True, blank=True)

    # ssl ignore for host or url
    ignore_ssl_verification = models.BooleanField(default=False)

    #response
    raw_response=models.TextField(null=True,blank=True)
    json_response=models.TextField(null=True,blank=True)

    # Basic Auth
    use_basic_auth = models.BooleanField(default=False)
    username = models.CharField(null=True,blank=True, max_length=256)
    password = models.CharField(null=True,blank=True, max_length=256)

    # status values
    up_value = models.CharField(null=True,blank=True, max_length=200)
    warn_value = models.CharField(null=True,blank=True, max_length=200)
    down_value = models.CharField(null=True,blank=True, max_length=200)

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

class ManualCheck(models.Model):
    check_name = models.CharField(max_length=50)
    check_url = models.CharField(max_length=255, default='', null=True, blank=True)
    notes = models.TextField(null=True,blank=True)
    system_id = models.CharField(max_length=50, default='',null=True, blank=True)
    group_responsible = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return self.check_name 
    
    def system_registry_url(self):
        system_id_url = ''
        if settings.IT_SYSTEM_REGISTER:
            if self.system_id:
                system_id_url = settings.IT_SYSTEM_REGISTER+'&q='+self.system_id
        return system_id_url
    

class NotificationEmail(models.Model):
    email = models.CharField(max_length=255, default='', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return self.email 
    

class TicketFilter(models.Model):
    name = models.CharField(max_length=255, default='', null=True, blank=True)
    url = models.CharField(max_length=2000, default='', null=True, blank=True)
    active = models.BooleanField(default=True) 
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name    
    
class TicketFilterNotification(models.Model):
    ticket_filter = models.ForeignKey(TicketFilter, null=True, blank=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=255, default='', null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email    

class NewTicketFilterNotification(models.Model):
    ticket_filter = models.ForeignKey(TicketFilter, null=True, blank=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=255, default='', null=True, blank=True)    
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email        

class Tickets(models.Model):
    ticket_reference_no = models.CharField(max_length=255, default='', null=True, blank=True)
    last_update_str = models.CharField(max_length=50, default='', null=True, blank=True)   
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_reference_no


class Platform(models.Model):

    system_name = models.CharField(max_length=255, default='', null=True, blank=True)
    api_key = models.CharField(max_length=512,null=True, blank=True, default='', help_text="Key is auto generated,  Leave blank or blank out to create a new key")
    operating_system_name = models.CharField(max_length=255, default='', null=True, blank=True)
    operating_system_version = models.CharField(max_length=255, default='', null=True, blank=True)
    python_version = models.CharField(max_length=255, default='', null=True, blank=True)
    django_version = models.CharField(max_length=255, default='', null=True, blank=True)    
    group_responsible = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)     
    vulnerability_total = models.IntegerField(default=0)
    json_response =  models.JSONField(null=True, blank=True)    
    stale_packages = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    last_sync_dt = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.system_name      

    def save(self, *args, **kwargs):
        if self.api_key is not None:

             if len(self.api_key) > 1:
                  pass
             else:
                  self.api_key = self.get_random_key(100)
        else:
            self.api_key = self.get_random_key(100)
        self.updated = datetime.now()
        #self.stale_packages = True
        super(Platform,self).save(*args,**kwargs)


    def get_random_key(self,key_length=100):
        return get_random_string(length=key_length, allowed_chars=u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')       

class PlatformAdvisoryEmail(models.Model):
    platform = models.ForeignKey(Platform, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.CharField(max_length=255, default='', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return self.email 

class PythonPackage(models.Model):
    
    package_name = models.CharField(max_length=255, default='', null=True, blank=True)
    current_package_version = models.CharField(max_length=255, default='', null=True, blank=True)
    platform = models.ForeignKey(Platform, null=True, blank=True, on_delete=models.SET_NULL)
    vulnerability_total = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_name
    
    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        print ("Updating Vulnerability Count")
        python_package_vunerability_version_advisory_information_obj = 0
        if PythonPackageVulnerability.objects.filter(package_name=self.package_name).count() > 0:
            python_package_vunerability_obj = PythonPackageVulnerability.objects.get(package_name=self.package_name)            
            if python_package_vunerability_obj:
                python_package_vunerability_version_obj = PythonPackageVulnerabilityVersion.objects.filter(python_package=python_package_vunerability_obj,package_version=self.current_package_version)

                if python_package_vunerability_version_obj.count() > 0:
                    python_package_vunerability_version_advisory_information_obj = PythonPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=python_package_vunerability_version_obj[0]).count()


        self.vulnerability_total = python_package_vunerability_version_advisory_information_obj

        vulnerability_total = 0
        if PythonPackage.objects.filter(platform=self.platform).count() > 0:
            pp_sum = PythonPackage.objects.filter(platform=self.platform).aggregate(Sum('vulnerability_total'))
            vulnerability_total = pp_sum['vulnerability_total__sum']
            

        platform = Platform.objects.get(id=self.platform.id)
        platform.vulnerability_total = pp_sum['vulnerability_total__sum']
        platform.save()

        #vulnerability_total        
        super(PythonPackage,self).save(*args,**kwargs)

class PythonPackageVersionHistory(models.Model):
    
    python_package = models.ForeignKey(PythonPackage, null=True, blank=True, on_delete=models.SET_NULL)     
    package_version = models.CharField(max_length=255, default='', null=True, blank=True)    
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_version          
    
class PythonPackageVulnerability(models.Model):
    package_name = models.CharField(max_length=255, default='', null=True, blank=True,unique=True)
    vulnerability_json =  models.JSONField(null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(PythonPackageVulnerability,self).save(*args,**kwargs)

class PythonPackageVulnerabilityVersion(models.Model):
    python_package = models.ForeignKey(PythonPackageVulnerability, null=True, blank=True, on_delete=models.SET_NULL)
    package_version = models.CharField(max_length=255, default='', null=True, blank=True) 
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.python_package.package_name+':'+self.package_version

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(PythonPackageVulnerabilityVersion,self).save(*args,**kwargs)

class PythonPackageVulnerabilityVersionAdvisoryInformation(models.Model):
    package_version = models.ForeignKey(PythonPackageVulnerabilityVersion, null=True, blank=True, on_delete=models.SET_NULL)
    advisory = models.TextField(default='', null=True, blank=True)
    cve = models.CharField(max_length=255, default='', null=True, blank=True) 
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_version.package_version

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(PythonPackageVulnerabilityVersionAdvisoryInformation,self).save(*args,**kwargs)

        python_package_obj = PythonPackage.objects.filter(package_name=self.package_version.python_package.package_name,current_package_version=self.package_version.package_version)

        for pp in python_package_obj:            
            pp.save()

            from appmonitor import email_templates
            t = email_templates.NewAdvisory()
            t.subject = "Python Advisory for package {}:{}".format(self.package_version.python_package.package_name, self.package_version.package_version)
            to_addresses=[]

            for notification in PlatformAdvisoryEmail.objects.filter(platform=pp.platform):
                print ("Preparing to "+notification.email)
                to_addresses.append(notification.email)
            t.send(to_addresses=to_addresses, context={"advisory" : self,"settings": settings, 'pp': pp}, headers={"Reply-To": settings.IT_CHECKS_REPLY_TO_EMAIL})    

        
