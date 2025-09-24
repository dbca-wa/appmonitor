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
        insecure_db_dir = str(settings.BASE_DIR) + '/db/npm_insecure/'
        INSECURE_NPM_LIST_FULL='https://github.com/github/advisory-database/archive/refs/heads/main.zip'
       
        if settings.INSECURE_NPM_LIST_FULL:
            INSECURE_NPM_LIST_FULL=settings.INSECURE_NPM_LIST_FULL        
            
        ziplocation = "/tmp/npm_security_notices.zip"
        extract_to_path = "/tmp/npm_security_notices/"
        # insecure_full_file = requests.get(INSECURE_UBUNTU_LIST_FULL)
        print (f"Downloading full insecure NPM vulnerabilities database from {INSECURE_NPM_LIST_FULL}...")
        
        http = urllib3.PoolManager()            
        with open(ziplocation, 'wb') as out:
            r = http.request('GET', INSECURE_NPM_LIST_FULL, preload_content=False)
            shutil.copyfileobj(r, out)

        print ("Download complete. Extracting files...")
        # with zipfile.ZipFile(ziplocation, 'r') as zip_ref:
        #     # Extract all contents to the specified directory
        #     zip_ref.extractall(extract_to_path)

        with zipfile.ZipFile(ziplocation, 'r') as zf:
            for member in zf.infolist():
                # Skip directories
                if member.is_dir():
                    continue

                # Construct the full path for the extracted file
                target_path = extract_to_path+f"/{member.filename}"

                # Ensure parent directories exist
                import os
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                with zf.open(member) as source_file:
                    with open(target_path, 'wb') as dest_file:
                        while True:
                            chunk = source_file.read(65536)
                            if not chunk:
                                break
                            dest_file.write(chunk)

            shutil.rmtree(insecure_db_dir, ignore_errors=True)
            os.makedirs(insecure_db_dir, exist_ok=True)
            print ("Extraction complete. Moving files to the database directory...")
            for i in os.listdir("/tmp/npm_security_notices/advisory-database-main/advisories/github-reviewed/"):
                print("/tmp/npm_security_notices/advisory-database-main/advisories/github-reviewed", i)
                shutil.move(os.path.join("/tmp/npm_security_notices/advisory-database-main/advisories/github-reviewed/", i), insecure_db_dir)
            shutil.rmtree("/tmp/npm_security_notices/")
            print ("Files moved successfully. Full insecure NPM vulnerabilities database update complete.")
       

# create a management script to update the vulnerabilities database and save local

#