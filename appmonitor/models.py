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

class ResponsibleGroupAccessUser(models.Model):
    responsible_group = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.CharField(max_length=255, default='', null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return self.email 

class ResponsibleGroupAccessGroup(models.Model):
    responsible_group = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, null=True,blank=True)

    def __str__(self):
        return self.group.name if self.group else 'No Group' 

class AccessGroup(models.Model):
    
    ACCESS_TYPE = Choices(
             (1, 'view_access', ('View Monitoring Status')),
             (2, 'edit_access', ('Create and Edit Access Platforms')), 
             (3, 'view_access_platform_status', ('View Access Platform Status')),
             (4, 'view_access_package_status', ('View Access Package Status')),
             (5, 'edit_access_monitoring', ('Edit Monitoring')),
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
             (9, 'http_status_code', ('HTTP Status Code')),
             (10, 'sharepoint_auth_check', ('SharePoint Auth Check')),
             (11, 'db_query_timing', ('DB Timing')),
             (12, 'db_query_check', ('DB Query')),
    )

    CHECK_OPERATOR = Choices(
             (1, 'postive', ('Positive Integer')),  
             (2, 'negative', ('Negative Integer')),  
             (3, 'equal_int', ('Equal Integer')),
             (4, 'equal_string', ('Equal String'))
    )

    DB_TYPE = Choices(
             (1, 'postgres', ('Postgres')),  
    )

    RESPONSE_TYPE = Choices(
             (1, 'OC', ('On Call')),  
             (2, 'BH', ('Business Hours')),               
    )

    # name for every check type
    check_name = models.CharField(max_length=50)
    mon_type = models.IntegerField(choices=MON_TYPE, null=True, blank=True, default=MON_TYPE.webconnect)
    response_type = models.IntegerField(choices=RESPONSE_TYPE, null=True, blank=True, default=RESPONSE_TYPE.OC)
    check_operator = models.IntegerField(choices=CHECK_OPERATOR, null=True, blank=True, default=CHECK_OPERATOR.postive)
    system_id = models.CharField(max_length=50, default='',null=True, blank=True)
    group_responsible = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)     
    use_auth2_token = models.BooleanField(default=False)
    timeout = models.IntegerField(default=30)

    # web connect (string key word checks)
    url = models.CharField(max_length=2048, default='', null=True, blank=True)
    string_check = models.CharField(max_length=50, null=True, blank=True)
    json_key = models.CharField(max_length=400, null=True, blank=True)
    status_code = models.IntegerField(default=200, null=True, blank=True)

    # port
    host = models.CharField(max_length=2048, default='', null=True, blank=True)
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

    # sharepoint auth check
    sharepoint_url =  models.CharField(null=True,blank=True, max_length=1024)
    sharepoint_username = models.CharField(null=True,blank=True, max_length=256)
    sharepoint_password = models.CharField(null=True,blank=True, max_length=256)

    db_type = models.IntegerField(choices=DB_TYPE, null=True, blank=True, default=DB_TYPE.postgres)
    db_host = models.CharField(null=True,blank=True, max_length=1024)
    db_name = models.CharField(null=True,blank=True, max_length=1024)
    db_username = models.CharField(null=True,blank=True, max_length=1024)
    db_password = models.CharField(null=True,blank=True, max_length=1024)
    db_port = models.CharField(null=True,blank=True, max_length=20)
    db_query = models.TextField(null=True,blank=True)

    # status values
    up_value = models.CharField(null=True,blank=True, max_length=200)
    warn_value = models.CharField(null=True,blank=True, max_length=200)
    down_value = models.CharField(null=True,blank=True, max_length=200)

    # Help Documentation
    help_doc = models.CharField(null=True,blank=True, max_length=2048)
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

class MonitorAlert(models.Model):
    monitor = models.ForeignKey(Monitor, null=True, blank=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=1024)
    no_html_email = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email    

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

class TicketSystem(models.Model):
    system_name = models.CharField(max_length=255, default='', null=True, blank=True)
    system_id = models.CharField(max_length=50, default='', null=True, blank=True)   
    freskdesk_system_id = models.IntegerField(default=0, null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.system_name

class TicketStatus(models.Model):
    status_name = models.CharField(max_length=255, default='', null=True, blank=True)    
    freskdesk_status_id = models.IntegerField(default=0, null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status_name

class Platform(models.Model):

    system_name = models.CharField(max_length=255, default='', null=True, blank=True)
    api_key = models.CharField(max_length=512,null=True, blank=True, default='', help_text="Key is auto generated,  Leave blank or blank out to create a new key")
    operating_system_name = models.CharField(max_length=255, default='', null=True, blank=True)
    operating_system_version = models.CharField(max_length=255, default='', null=True, blank=True)
    python_version = models.CharField(max_length=255, default='', null=True, blank=True)
    django_version = models.CharField(max_length=255, default='', null=True, blank=True)    
    git_repo_name = models.CharField(max_length=512, default='', null=True, blank=True)  
    group_responsible = models.ForeignKey(ResponsibleGroup, null=True, blank=True, on_delete=models.SET_NULL)     
    vulnerability_total = models.IntegerField(default=0)
    vulnerability_total_debian = models.IntegerField(default=0,null=True)
    vulnerability_total_npm = models.IntegerField(default=0,null=True)    
    platform_current_severity = models.CharField(max_length=20, default='', null=True, blank=True)
    dependabot_vulnerability_total = models.IntegerField(default=0)
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

class PlatformDependaBotAdvisory(models.Model):
    
    platform = models.ForeignKey(Platform, null=True, blank=True, on_delete=models.SET_NULL)  
    number = models.IntegerField(null=True, blank=True) 
    state = models.CharField(max_length=20, default='', null=True, blank=True)
    ghsa_id = models.CharField(max_length=255, default='', null=True, blank=True)
    package_name = models.CharField(max_length=255, default='', null=True, blank=True)
    ecosystem = models.CharField(max_length=255, default='', null=True, blank=True)
    severity = models.CharField(max_length=20, default='', null=True, blank=True)
    cve_id = models.CharField(max_length=50, default='', null=True, blank=True)    
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_name

class DebianPackage(models.Model):
    
    platform = models.ForeignKey(Platform, null=True, blank=True, on_delete=models.SET_NULL)
    package_name = models.CharField(max_length=255, default='', null=True, blank=True)
    current_package_version = models.CharField(max_length=255, default='', null=True, blank=True)    
    vulnerability_total = models.IntegerField(default=0,null=True)
    severity_rollup = models.CharField(max_length=40, default='', null=True, blank=True)
    active = models.BooleanField(default=True,null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_name
    
    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        print ("Updating Vulnerability Count")
        print ("Updating Vulnerability Count")
        print ("Updating Vulnerability Count")
        print ("Updating Vulnerability Count")

        debian_package_vunerability_version_advisory_information_obj = 0
        current_severity = ""
        
        if DebianPackageVulnerability.objects.filter(package_name=self.package_name).count() > 0:
            print ("Updating Vulnerability Count"+self.package_name)
            debian_package_vunerability_obj = DebianPackageVulnerability.objects.get(package_name=self.package_name)            
            if debian_package_vunerability_obj:
                debian_package_vunerability_version_obj = DebianPackageVulnerabilityVersion.objects.filter(debian_package=debian_package_vunerability_obj,package_version=self.current_package_version)

                if debian_package_vunerability_version_obj.count() > 0:
                    ppvai_obj = DebianPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=debian_package_vunerability_version_obj[0])
                    debian_package_vunerability_version_advisory_information_obj = ppvai_obj.count()
                    
                    for ppvai in ppvai_obj:                                                                        
                        if ppvai.baseSeverity == 'LOW':         
                            if current_severity == "MEDIUM" or current_severity == "HIGH" or current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity                                                   
                        if ppvai.baseSeverity == 'MEDIUM':
                            if current_severity == "HIGH" or current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity
                        if ppvai.baseSeverity == 'HIGH':
                            if current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity
                        if ppvai.baseSeverity == 'CRITICAL':                            
                            current_severity = ppvai.baseSeverity                                                                        
                    
        self.severity_rollup = current_severity
        self.vulnerability_total = debian_package_vunerability_version_advisory_information_obj
        print ("Updating Vulnerability Count"+str(self.vulnerability_total))
        print ("Updating Vulnerability Count"+str(self.severity_rollup))
        # vulnerability_total_python = 0
        # if PythonPackage.objects.filter(platform=self.platform).count() > 0:
        #     pp_sum = PythonPackage.objects.filter(platform=self.platform, active=True).aggregate(Sum('vulnerability_total'))
        #     if pp_sum['vulnerability_total__sum'] is not None:
        #         vulnerability_total_python = pp_sum['vulnerability_total__sum']
        vulnerability_total_debian = 0
        if DebianPackage.objects.filter(platform=self.platform).count() > 0:
            pp_sum = DebianPackage.objects.filter(platform=self.platform, active=True).aggregate(Sum('vulnerability_total'))
            if pp_sum['vulnerability_total__sum'] is not None:
                vulnerability_total_debian = pp_sum['vulnerability_total__sum']                
            
        # vulnerability_total = vulnerability_total_python + vulnerability_total_debian
        platform = Platform.objects.get(id=self.platform.id)
        # platform.vulnerability_total = vulnerability_total
        platform.vulnerability_total_debian = vulnerability_total_debian
        platform.save()        

        super(DebianPackage,self).save(*args,**kwargs)

class DebianPackageVersionHistory(models.Model):
    
    debian_package = models.ForeignKey(DebianPackage, null=True, blank=True, on_delete=models.SET_NULL)     
    package_version = models.CharField(max_length=255, default='', null=True, blank=True)    
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_version   

class DebianPackageVulnerability(models.Model):
    package_name = models.CharField(max_length=255, default='', null=True, blank=True,unique=True)
    vulnerability_json =  models.JSONField(null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(DebianPackageVulnerability,self).save(*args,**kwargs)

    def __str__(self):

        if self.package_name:
            return self.package_name       
        else:
            return "No Package Name"

class DebianPackageVulnerabilityVersion(models.Model):
    debian_package = models.ForeignKey(DebianPackageVulnerability, null=True, blank=True, on_delete=models.SET_NULL)
    package_version = models.CharField(max_length=255, default='', null=True, blank=True) 
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.debian_package:
            if self.debian_package.package_name:
                return self.debian_package.package_name + ':' + self.package_version
            else:
                return 'No Package Name' + ':' + self.package_version
        return 'No Debian Package'
        #return self.debian_package.package_name+':'+self.package_version

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(DebianPackageVulnerabilityVersion,self).save(*args,**kwargs)

class DebianPackageVulnerabilityVersionAdvisoryInformation(models.Model):
    package_version = models.ForeignKey(DebianPackageVulnerabilityVersion, null=True, blank=True, on_delete=models.SET_NULL)
    advisory = models.TextField(default='', null=True, blank=True)
    cve = models.CharField(max_length=255, default='', null=True, blank=True) 
    baseSeverity = models.CharField(max_length=40, default='', null=True, blank=True)
    baseScore = models.FloatField(default='0', null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_version.package_version

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(DebianPackageVulnerabilityVersionAdvisoryInformation,self).save(*args,**kwargs)

        if self.package_version:
            if self.package_version.debian_package:
                python_package_obj = DebianPackage.objects.filter(package_name=self.package_version.debian_package.package_name,current_package_version=self.package_version.package_version)

                for pp in python_package_obj:            
                    pp.save()

                    # from appmonitor import email_templates
                    # t = email_templates.NewAdvisory()
                    # t.subject = "Python Advisory for package {}:{}".format(self.package_version.debian_package.package_name, self.package_version.package_version)
                    # to_addresses=[]

                    # for notification in PlatformAdvisoryEmail.objects.filter(platform=pp.platform):
                    #     print ("Preparing to "+notification.email)
                    #     to_addresses.append(notification.email)
                    # t.send(to_addresses=to_addresses, context={"advisory" : self,"settings": settings, 'pp': pp}, headers={"Reply-To": settings.IT_CHECKS_REPLY_TO_EMAIL})    

                    # if pp.platform.group_responsible:
                    #     for notification in ResponsibleGroupAdvisoryEmail.objects.filter(id=pp.platform.group_responsible.id,active=True):
                    #         print ("Preparing to "+notification.email)
                    #         to_addresses.append(notification.email)
                    #     t.send(to_addresses=to_addresses, context={"advisory" : self,"settings": settings, 'pp': pp}, headers={"Reply-To": settings.IT_CHECKS_REPLY_TO_EMAIL})    

class NpmPackage(models.Model):
    
    platform = models.ForeignKey(Platform, null=True, blank=True, on_delete=models.SET_NULL)
    package_name = models.CharField(max_length=255, default='', null=True, blank=True)
    source_file = models.CharField(max_length=2048, default='', null=True, blank=True)
    current_package_version = models.CharField(max_length=255, default='', null=True, blank=True)    
    vulnerability_total = models.IntegerField(default=0,null=True)
    severity_rollup = models.CharField(max_length=40, default='', null=True, blank=True)
    active = models.BooleanField(default=True,null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_name
    
    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        print ("Updating Vulnerability Count")
        print ("Updating Vulnerability Count")
        print ("Updating Vulnerability Count")
        print ("Updating Vulnerability Count")

        npm_package_vunerability_version_advisory_information_obj = 0
        current_severity = ""
        
        if NpmPackageVulnerability.objects.filter(package_name=self.package_name).count() > 0:
            print ("Updating Vulnerability Count"+self.package_name)
            npm_package_vunerability_obj = NpmPackageVulnerability.objects.get(package_name=self.package_name)            
            if npm_package_vunerability_obj:
                npm_package_vunerability_version_obj = NpmPackageVulnerabilityVersion.objects.filter(npm_package=npm_package_vunerability_obj,package_version=self.current_package_version)

                if npm_package_vunerability_version_obj.count() > 0:
                    ppvai_obj = NpmPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=npm_package_vunerability_version_obj[0])
                    npm_package_vunerability_version_advisory_information_obj = ppvai_obj.count()
                    
                    for ppvai in ppvai_obj:                                                                        
                        if ppvai.baseSeverity == 'LOW':         
                            if current_severity == "MEDIUM" or current_severity == "HIGH" or current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity                                                   
                        if ppvai.baseSeverity == 'MEDIUM':
                            if current_severity == "HIGH" or current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity
                        if ppvai.baseSeverity == 'HIGH':
                            if current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity
                        if ppvai.baseSeverity == 'CRITICAL':                            
                            current_severity = ppvai.baseSeverity                                                                        
                    
        self.severity_rollup = current_severity
        self.vulnerability_total = npm_package_vunerability_version_advisory_information_obj
        print ("Updating Vulnerability Count"+str(self.vulnerability_total))
        print ("Updating Vulnerability Count"+str(self.severity_rollup))
        # vulnerability_total_python = 0
        # if PythonPackage.objects.filter(platform=self.platform).count() > 0:
        #     pp_sum = PythonPackage.objects.filter(platform=self.platform, active=True).aggregate(Sum('vulnerability_total'))
        #     if pp_sum['vulnerability_total__sum'] is not None:
        #         vulnerability_total_python = pp_sum['vulnerability_total__sum']
        vulnerability_total_npm = 0
        if NpmPackage.objects.filter(platform=self.platform).count() > 0:
            pp_sum = NpmPackage.objects.filter(platform=self.platform, active=True).aggregate(Sum('vulnerability_total'))
            if pp_sum['vulnerability_total__sum'] is not None:
                vulnerability_total_npm = pp_sum['vulnerability_total__sum']                
            
        # vulnerability_total = vulnerability_total_python + vulnerability_total_debian
        platform = Platform.objects.get(id=self.platform.id)
        # platform.vulnerability_total = vulnerability_total
        platform.vulnerability_total_npm = vulnerability_total_npm
        platform.save()        

        super(NpmPackage,self).save(*args,**kwargs)

class NpmPackageVersionHistory(models.Model):
    
    npm_package = models.ForeignKey(NpmPackage, null=True, blank=True, on_delete=models.SET_NULL)     
    package_version = models.CharField(max_length=255, default='', null=True, blank=True)    
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_version

class NpmPackageVulnerability(models.Model):
    package_name = models.CharField(max_length=255, default='', null=True, blank=True,unique=True)
    vulnerability_json =  models.JSONField(null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(NpmPackageVulnerability,self).save(*args,**kwargs)

    def __str__(self):

        if self.package_name:
            return self.package_name       
        else:
            return "No Package Name"

class NpmPackageVulnerabilityVersion(models.Model):
    npm_package = models.ForeignKey(NpmPackageVulnerability, null=True, blank=True, on_delete=models.SET_NULL)
    package_version = models.CharField(max_length=255, default='', null=True, blank=True) 
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.npm_package:
            if self.npm_package.package_name:
                return self.npm_package.package_name + ':' + self.package_version
            else:
                return 'No Package Name' + ':' + self.package_version
        return 'No Debian Package'
        #return self.debian_package.package_name+':'+self.package_version

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(NpmPackageVulnerabilityVersion,self).save(*args,**kwargs)

class NpmPackageVulnerabilityVersionAdvisoryInformation(models.Model):
    package_version = models.ForeignKey(NpmPackageVulnerabilityVersion, null=True, blank=True, on_delete=models.SET_NULL)
    advisory = models.TextField(default='', null=True, blank=True)
    cve = models.CharField(max_length=255, default='', null=True, blank=True) 
    baseSeverity = models.CharField(max_length=40, default='', null=True, blank=True)
    baseScore = models.FloatField(default='0', null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_version.package_version

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        super(NpmPackageVulnerabilityVersionAdvisoryInformation,self).save(*args,**kwargs)

        if self.package_version:
            if self.package_version.npm_package:
                python_package_obj = NpmPackage.objects.filter(package_name=self.package_version.npm_package.package_name,current_package_version=self.package_version.package_version)

                for pp in python_package_obj:            
                    pp.save()

class PythonPackage(models.Model):
    
    package_name = models.CharField(max_length=255, default='', null=True, blank=True)
    current_package_version = models.CharField(max_length=255, default='', null=True, blank=True)
    platform = models.ForeignKey(Platform, null=True, blank=True, on_delete=models.SET_NULL)
    vulnerability_total = models.IntegerField(default=0,null=True)
    severity_rollup = models.CharField(max_length=40, default='', null=True, blank=True)
    active = models.BooleanField(default=True,null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.package_name
    
    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        print ("Updating Vulnerability Count")
        python_package_vunerability_version_advisory_information_obj = 0
        current_severity = ""
        if PythonPackageVulnerability.objects.filter(package_name=self.package_name).count() > 0:
            python_package_vunerability_obj = PythonPackageVulnerability.objects.get(package_name=self.package_name)            
            if python_package_vunerability_obj:
                python_package_vunerability_version_obj = PythonPackageVulnerabilityVersion.objects.filter(python_package=python_package_vunerability_obj,package_version=self.current_package_version)

                if python_package_vunerability_version_obj.count() > 0:
                    ppvai_obj = PythonPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=python_package_vunerability_version_obj[0])
                    python_package_vunerability_version_advisory_information_obj = ppvai_obj.count()
                    
                    for ppvai in ppvai_obj:                                                                        
                        if ppvai.baseSeverity == 'LOW':         
                            if current_severity == "MEDIUM" or current_severity == "HIGH" or current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity                                                   
                        if ppvai.baseSeverity == 'MEDIUM':
                            if current_severity == "HIGH" or current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity
                        if ppvai.baseSeverity == 'HIGH':
                            if current_severity == "CRITICAL":
                                pass
                            else:
                                current_severity = ppvai.baseSeverity
                        if ppvai.baseSeverity == 'CRITICAL':                            
                            current_severity = ppvai.baseSeverity                                                                        
                    
        self.severity_rollup = current_severity
        self.vulnerability_total = python_package_vunerability_version_advisory_information_obj

        vulnerability_total_python = 0
        if PythonPackage.objects.filter(platform=self.platform).count() > 0:
            pp_sum = PythonPackage.objects.filter(platform=self.platform, active=True).aggregate(Sum('vulnerability_total'))
            if pp_sum['vulnerability_total__sum'] is not None:
                vulnerability_total_python = pp_sum['vulnerability_total__sum']
                
        # vulnerability_total_debian = 0
        # if DebianPackage.objects.filter(platform=self.platform).count() > 0:
        #     pp_sum = DebianPackage.objects.filter(platform=self.platform, active=True).aggregate(Sum('vulnerability_total'))
        #     if pp_sum['vulnerability_total__sum'] is not None:
        #         vulnerability_total_debian = pp_sum['vulnerability_total__sum']                           
        # vulnerability_total = vulnerability_total_python + vulnerability_total_debian
        
        platform = Platform.objects.get(id=self.platform.id)
        platform.vulnerability_total = vulnerability_total_python
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

    def __str__(self):
        return self.package_name            

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
    baseSeverity = models.CharField(max_length=40, default='', null=True, blank=True)
    baseScore = models.FloatField(default='0', null=True, blank=True)
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

            # for notification in PlatformAdvisoryEmail.objects.filter(platform=pp.platform):
            #     print ("Preparing to "+notification.email)
            #     to_addresses.append(notification.email)
            # t.send(to_addresses=to_addresses, context={"advisory" : self,"settings": settings, 'pp': pp}, headers={"Reply-To": settings.IT_CHECKS_REPLY_TO_EMAIL})    

            # if pp.platform.group_responsible:
            #     for notification in ResponsibleGroupAdvisoryEmail.objects.filter(id=pp.platform.group_responsible.id,active=True):
            #         print ("Preparing to "+notification.email)
            #         to_addresses.append(notification.email)
            #     t.send(to_addresses=to_addresses, context={"advisory" : self,"settings": settings, 'pp': pp}, headers={"Reply-To": settings.IT_CHECKS_REPLY_TO_EMAIL})    


            
