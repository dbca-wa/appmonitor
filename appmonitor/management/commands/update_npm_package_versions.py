from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
from datetime import datetime
import requests
import urllib3
import os
import zipfile
import shutil
import time
import subprocess
from appmonitor import models

class Command(BaseCommand):
    help = 'Update the NPM vulnerabilities database.'

    def add_arguments(self, parser):
        parser.add_argument('-a' '--action', type=str , help='Select an action')

    def handle(self, *args, **options):
        print ("Running NPM Insecure DB Update.")
        current_date_time = datetime.now()
        current_year = current_date_time.strftime("%Y")
        action = options['a__action']
        insecure_db_dir = str(settings.BASE_DIR) + '/db/npm_versions'

        npm_packages = models.NpmPackage.objects.filter(active=True).order_by('-id')
        
        os.makedirs(insecure_db_dir, exist_ok=True)
        
        for n in npm_packages:
            package_prefix = n.package_name[:2]
            package_store_path = insecure_db_dir+'/'+package_prefix
            #print (n.package_name)
            
            os.makedirs(package_store_path, exist_ok=True)
            full_file_path = package_store_path+"/"+n.package_name+".json"
            
            if "/" in n.package_name:
                package_name_first = n.package_name.split("/")[0]
                #print (package_name_first)
                os.makedirs(package_store_path+"/"+package_name_first, exist_ok=True)
            
            if not os.path.exists(full_file_path):
                print ("npm show '"+n.package_name+"' versions --json > "+full_file_path)
                result = subprocess.run("npm show '"+n.package_name+"' versions --json > "+full_file_path, shell=True)
            else:
                modification_timestamp = os.path.getmtime(full_file_path)

                # Get the current time in seconds since the epoch
                current_time = time.time()

                # Calculate the age of the file in seconds
                file_age_seconds = current_time - modification_timestamp
                if file_age_seconds > 345600: # 4 Days  (so we dont hammer the npm registry) 
                    print ("npm show '"+n.package_name+"' versions --json > "+full_file_path)
                    result = subprocess.run("npm show '"+n.package_name+"' versions --json > "+full_file_path, shell=True)
                #print (modification_timestamp, file_age_seconds)
           
   

            
            
            

        
       

# create a management script to update the vulnerabilities database and save local

#