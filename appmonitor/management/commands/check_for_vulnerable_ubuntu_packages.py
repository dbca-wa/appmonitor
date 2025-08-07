import json
from appmonitor import utils
from datetime import datetime
from packaging.version import parse as parseVersion

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
import datetime
from appmonitor import models
from appmonitor import email_templates
import os

class Command(BaseCommand):
    help = 'Check for package security issues.'

    def handle(self, *args, **options):
        
        ubuntu_insecure_path = str(settings.BASE_DIR) + '/db/ubuntu_insecure/'

        error_row = []
        try:
            # python_pacakges_obj = models.DebianPackage.objects.all().values_list('package_name', flat=True).distinct()
            # total_package_count = python_pacakges_obj.count()
            # print (total_package_count)
            # loop through ./db/ubuntu_insecure/ folders and files and read them            
            folders = []
            for item in os.listdir(ubuntu_insecure_path):
                item_path = os.path.join(ubuntu_insecure_path, item)
                if os.path.isdir(item_path):
                    
                    for item2 in os.listdir(ubuntu_insecure_path+item):
                        print (item2)
                        opened_file = open(ubuntu_insecure_path+item+'/'+item2, "r")
                        insecure_full = opened_file.read()
                        insecure_full_json  = json.loads(insecure_full)
                        opened_file.close()
                        for i in insecure_full_json['affected']:
                            #print (i["package"]["name"])
                            deb_pack = models.DebianPackage.objects.filter(package_name=i["package"]["name"])
                            if deb_pack.count() > 0:
                                print ("Found Package: " + i["package"]["name"])
                                for v in i["versions"]:

                                    print (deb_pack[0].current_package_version)

                                    if deb_pack[0].current_package_version == v:

                                        ppv = None
                                        if models.DebianPackageVulnerability.objects.filter(package_name=i["package"]["name"]).count() > 0:
                                            pass
                                            ppv = models.DebianPackageVulnerability.objects.get(package_name=i["package"]["name"])
                                            #ppv.save()
                                        else:
                                            ppv = models.DebianPackageVulnerability.objects.create(package_name=i["package"]["name"])

                                        ppvv = None
                                        if models.DebianPackageVulnerabilityVersion.objects.filter(debian_package=ppv,package_version=v).count() > 0:

                                            ppvv = models.DebianPackageVulnerabilityVersion.objects.get(debian_package=ppv,package_version=v)
                                        else:

                                            ppvv = models.DebianPackageVulnerabilityVersion.objects.create(debian_package=ppv,package_version=v)

                                        cve = ''
                                        if "related" in insecure_full_json:
                                            if len(insecure_full_json['related']) > 0:
                                                cve = insecure_full_json['related'][0]
                                        if "upstream" in insecure_full_json:
                                            if len(insecure_full_json['upstream']) > 0:
                                                cve = insecure_full_json['upstream'][0]                                            
                                        print (cve)
                                        advisory_info = ''
                                        if "details" in insecure_full_json:                                            
                                            advisory_info = insecure_full_json['details']                                                                                    

                                        ppvvai = None
                                        if models.DebianPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=ppvv,cve=cve).count() > 0:
                                            ppvvai = models.DebianPackageVulnerabilityVersionAdvisoryInformation.objects.get(package_version=ppvv,cve=cve)
                                        else:
                                            ppvvai = models.DebianPackageVulnerabilityVersionAdvisoryInformation.objects.create(package_version=ppvv,cve=cve, advisory=advisory_info)

                        # FOLDER
                        folders.append(item2)
                #print (folders)



        except Exception as e:
            print("An error occurred while checking for vulnerable packages:")
            print(e)
            