from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models import Sum
import datetime
from appmonitor import models
import subprocess
import tarfile
import os
import shutil
import csv

class Command(BaseCommand):
    help = 'Scan docker images'

    def add_arguments(self, parser):
        parser.add_argument('-i' '--id', type=str , help='Only run selected platform by id', default=None)

    def handle(self, *args, **options):
        print ("Rebuilding Platform Packages...")
        
        
        try:
            DB_DIRECTORY_TO_ARCHIVE = settings.DB_DIRECTORY_TO_ARCHIVE
            os.makedirs(DB_DIRECTORY_TO_ARCHIVE+"/scans/", exist_ok=True)            
            pid = options['i__id']          
            if pid is None:
                platform_obj = models.Platform.objects.filter(active=True)  
            else:                         
                platform_obj = models.Platform.objects.filter(active=True, id=pid)

            for p in platform_obj:                

                if len(p.image_name) > 1 and len(p.image_tag) > 1:
                    print (p)  
                    print (p.image_name)
                    print (p.image_tag)  
                    if os.path.exists("/tmp/dockerimage-export.tar"):    
                        os.remove("/tmp/dockerimage-export.tar")
                    if os.path.isdir("/tmp/dockerimage/"):
                        shutil.rmtree("/tmp/dockerimage/")    
                    
                    result = subprocess.run(["skopeo", "copy", "docker://"+p.image_name+":"+p.image_tag,"docker-archive:/tmp/dockerimage-export.tar"], capture_output=True, text=True)           
                    print (result)
                    os.mkdir("/tmp/dockerimage/") 
                    with tarfile.open("/tmp/dockerimage-export.tar", "r") as tar:
                        tar.extractall(path="/tmp/dockerimage")

                    for root, dirs, files in os.walk("/tmp/dockerimage/"):
                        for file in files:
                            if file.endswith((".tar")):
                                archive_path = os.path.join(root, file)
                                extract_to = os.path.join(root, "/tmp/dockerimage/uncompressed")
                                os.makedirs(extract_to, exist_ok=True)

      

                                try:                                    
                                    with tarfile.open(archive_path, "r:*") as inner_tar:
                                        safe_members = [
                                            m for m in inner_tar.getmembers() 
                                            if not (m.issym() or m.islnk())
                                        ]
                                        inner_tar.extractall(path=extract_to, filter="data", members=safe_members)                        
                                except Exception as e:
                                    print ("EXCEPTION Extracting:")
                                    print (e)

                    result = subprocess.run(["syft", "dir:/tmp/dockerimage/uncompressed/","-o", "cyclonedx-json="+str(DB_DIRECTORY_TO_ARCHIVE)+"/scans/"+str(p.id)+"-sbom.json"], capture_output=True, text=True)           
                    print (result)

                    result = subprocess.run(["grype", str(DB_DIRECTORY_TO_ARCHIVE)+"/scans/"+str(p.id)+"-sbom.json", "--sort-by=severity", "--output=template","--template="+str(settings.BASE_DIR)+"/static-config/tsv.tmpl", "--file="+str(DB_DIRECTORY_TO_ARCHIVE)+"/scans/"+str(p.id)+"-vulnerabilities.csv"], capture_output=True, text=True)           
                    print (result)
                     
                    target_column = 'FixState'
                    target_value = 'fixed'
                    count = 0

                    with open(str(DB_DIRECTORY_TO_ARCHIVE)+"/scans/"+str(p.id)+"-vulnerabilities.csv", mode='r', encoding='utf-8') as file:
                        # Use delimiter='\t' for tab-separated, or delimiter=',' for standard CSV
                        reader = csv.DictReader(file, delimiter='\t')
                        
                        # Strip any accidental whitespace from headers
                        reader.fieldnames = [field.strip() for field in reader.fieldnames] if reader.fieldnames else []
                        
                        if target_column in reader.fieldnames:
                            for row in reader:
                                # Compare the cell value (stripping whitespace to handle formatting safely)
                                
                                if row[target_column].strip() == target_value:
                                    print (row[target_column].strip())
                                    count += 1
                            print(f"Total records where '{target_column}' is '{target_value}': {count}")
                            p.vulnerability_total_grype=count
                            p.save()
                        else:
                            print(f"Error: Column '{target_column}' not found. Available columns are: {reader.fieldnames}")
                    
        except Exception as e:
            print ("EXCEPTION2:")
            print (e)