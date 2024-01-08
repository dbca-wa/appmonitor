import json
from appmonitor import utils
from datetime import datetime
from packaging.version import parse as parseVersion

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
import datetime
import os
import requests
from appmonitor import models

class Command(BaseCommand):
    help = 'Check for package security issues.'

    def handle(self, *args, **options):
        
        try:
            python_pacakges_obj = models.PythonPackage.objects.all().values_list('package_name', flat=True).distinct()

            for pp in python_pacakges_obj:
                if os.path.isdir(str(settings.BASE_DIR)+'/python_packages_db/'+pp[0:1]) is False:
                    os.makedirs(str(settings.BASE_DIR)+'/python_packages_db/'+pp[0:1])
                if os.path.isdir(str(settings.BASE_DIR)+'/python_packages_db/'+pp[0:1]+'/'+pp[1:2]) is False:
                    os.makedirs(str(settings.BASE_DIR)+'/python_packages_db/'+pp[0:1]+'/'+pp[1:2])                
                print (pp)

                pipy_package_json = requests.get("https://pypi.org/pypi/"+pp+"/json")
                if pipy_package_json.status_code == 200:
                    with open(str(settings.BASE_DIR)+'/python_packages_db/'+pp[0:1]+'/'+pp[1:2]+'/'+pp+'.json', 'wb') as f:
                        f.write(pipy_package_json.content)


        except Exception as e:
            print (e)

