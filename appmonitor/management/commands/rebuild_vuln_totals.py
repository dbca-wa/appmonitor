from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.db.models import Sum
import datetime
from appmonitor import models

class Command(BaseCommand):
    help = 'Remove old logs.'

    def handle(self, *args, **options):
        print ("Rebuilding Platform Packages...")
        try:
            platform_obj = models.Platform.objects.filter(active=True)           

            for p in platform_obj:
                platform_json = p.json_response
                vulnerability_total_count = 0   
                platform_current_severity = ""     

                vulnerability_total_python = 0
                if models.PythonPackage.objects.filter(platform=p).count() > 0:
                    pp_sum = models.PythonPackage.objects.filter(platform=p, active=True).aggregate(Sum('vulnerability_total'))
                    if pp_sum['vulnerability_total__sum'] is not None:
                        vulnerability_total_python = pp_sum['vulnerability_total__sum']
                        
                vulnerability_total_debian = 0
                if models.DebianPackage.objects.filter(platform=p).count() > 0:
                    pp_sum = models.DebianPackage.objects.filter(platform=p, active=True).aggregate(Sum('vulnerability_total'))
                    if pp_sum['vulnerability_total__sum'] is not None:
                        vulnerability_total_debian = pp_sum['vulnerability_total__sum']                           
                

                vulnerability_total_npm = 0
                if models.NpmPackage.objects.filter(platform=p).count() > 0:
                    pp_sum = models.NpmPackage.objects.filter(platform=p, active=True).aggregate(Sum('vulnerability_total'))
                    if pp_sum['vulnerability_total__sum'] is not None:
                        vulnerability_total_npm = pp_sum['vulnerability_total__sum']                           
                             
                p.vulnerability_total_npm = vulnerability_total_npm
                p.vulnerability_total_debian = vulnerability_total_debian
                p.vulnerability_total = vulnerability_total_python
                p.save()


        except Exception as e:
            print ("EXCEPTION2:")
            print (e)