from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
from datetime import datetime
import requests
import os
import zipfile
import shutil
from appmonitor import models

class Command(BaseCommand):
    help = 'Update the Ubuntu vulnerabilities database.'

    def add_arguments(self, parser):
        parser.add_argument('-a' '--action', type=str , help='Select an action')

    def handle(self, *args, **options):
        print ("Running Ubuntu Insecure DB Update.")
        current_date_time = datetime.now()
        current_year = current_date_time.strftime("%Y")
        print (current_year)
        action = options['a__action']
        insecure_db_dir = str(settings.BASE_DIR) + '/db/ubuntu_insecure/'
        INSECURE_UBUNTU_LIST_FULL='https://github.com/canonical/ubuntu-security-notices/archive/refs/heads/main.zip'
        INSECURE_UBUNTU_LIST='https://api.github.com/repos/canonical/ubuntu-security-notices/contents/osv/cve'
        if settings.INSECURE_UBUNTU_LIST:
            INSECURE_UBUNTU_LIST=settings.INSECURE_UBUNTU_LIST
        if settings.INSECURE_UBUNTU_LIST_FULL:
            INSECURE_UBUNTU_LIST_FULL=settings.INSECURE_UBUNTU_LIST_FULL

        if action == 'full':
            
            ziplocation = "/tmp/ubuntu_security_notices.zip"
            extract_to_path = "/tmp/ubuntu_security_notices/"
            # insecure_full_file = requests.get(INSECURE_UBUNTU_LIST_FULL)
            print (f"Downloading full insecure Ubuntu vulnerabilities database from {INSECURE_UBUNTU_LIST_FULL}...")
            chunk_size = 8192
            with requests.get(INSECURE_UBUNTU_LIST_FULL, stream=True) as r:
                r.raise_for_status()  # Raise an exception for bad status codes
                with open(ziplocation, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:  # Filter out keep-alive new chunks
                            f.write(chunk)

            # f = open(ziplocation, 'wb')
            # for chunk in insecure_full_file.iter_content(chunk_size=512 * 1024): 
            #     if chunk: # filter out keep-alive new chunks
            #         f.write(chunk)
            # f.close()
            print ("Download complete. Extracting files...")
            with zipfile.ZipFile(ziplocation, 'r') as zip_ref:
                # Extract all contents to the specified directory
                zip_ref.extractall(extract_to_path)
            shutil.rmtree(insecure_db_dir, ignore_errors=True)
            os.makedirs(insecure_db_dir, exist_ok=True)
            print ("Extraction complete. Moving files to the database directory...")
            for i in os.listdir("/tmp/ubuntu_security_notices/ubuntu-security-notices-main/osv/cve/"):
                print("/tmp/ubuntu_security_notices/ubuntu-security-notices-main/osv/cve/", i)
                shutil.move(os.path.join("/tmp/ubuntu_security_notices/ubuntu-security-notices-main/osv/cve/", i), insecure_db_dir)
            shutil.rmtree("/tmp/ubuntu_security_notices/")
            print ("Files moved successfully. Full insecure Ubuntu vulnerabilities database update complete.")
        else:
            print ("Downloading insecure Ubuntu vulnerabilities database for current year...")
            insecure_list_json_string = requests.get(INSECURE_UBUNTU_LIST+"/"+current_year)
            if insecure_list_json_string.status_code == 200:
                json_list = insecure_list_json_string.json()
                for j in json_list:
                    # print (j["name"])
                    # print (j["type"])

                    if j["type"] == "dir":
                        os.makedirs(str(settings.BASE_DIR) + '/db/ubuntu_insecure/' + j["name"], exist_ok=True)
                        insecure_list_dir_json_string = requests.get(INSECURE_UBUNTU_LIST+j["name"])
                        print (insecure_list_dir_json_string.status_code)
                        if insecure_list_dir_json_string.status_code == 200:
                            json_file_list = insecure_list_dir_json_string.json()
                            for g in json_file_list:
                                if g["type"] == "file":
                                    print (g["download_url"])
                                    if os.path.exists(insecure_db_dir +"/"+ j["name"]+'/'+g["name"]):
                                        print(f"File {g['name']} already exists, skipping download.")
                                    else:
                                        cve_file = requests.get(g["download_url"])
                                        if cve_file.status_code == 200:
                                            cve_file_raw = cve_file.content
                                            with open(str(settings.BASE_DIR) + '/db/ubuntu_insecure/' + j["name"]+'/'+g["name"], "wb") as f:
                                                f.write(cve_file_raw)
                                                print(f"Saved {g["name"]} successfully.")     
                    if j["type"] == "file":                                                   
                        if os.path.exists(insecure_db_dir +"/"+ current_year +'/'+j["name"]):
                            pass
                            #print(f"File {j['name']} already exists, skipping download.")
                        else:
                            cve_file = requests.get(j["download_url"])
                            if cve_file.status_code == 200:
                                cve_file_raw = cve_file.content
                                with open(str(settings.BASE_DIR) + '/db/ubuntu_insecure/' + current_year+'/'+j["name"], "wb") as f:
                                    f.write(cve_file_raw)
                                    print(f"Saved {j["name"]} successfully.")                             


                    # if j["type"] == "file":
                    #     file_url = j["download_url"]
                    #     file_content = requests.get(file_url)
                    #     if file_content.status_code == 200:
                    #         file_name = j["name"]
                    #         with open(str(settings.BASE_DIR) + '/db/' + file_name, "wb") as f:
                    #             f.write(file_content.content)
                    #             print(f"Saved {file_name} successfully.")
                    #     else:
                    #         print(f"Failed to download {file_url}: {file_content.status_code}")

                # f = open(str(settings.BASE_DIR)+'/db/insecure_full.json', "wb")
                # f.write(insecure_list_json_string.content)
                # f.close()
                print ("Insecure DB Update Successful")
            else:
                print ("Insecure DB Update failed")
                print (insecure_list_json_string.status_code)
                print (insecure_list_json_string.content)





# create a management script to update the vulnerabilities database and save local

#