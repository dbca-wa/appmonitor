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
from semantic_version import NpmSpec, Version
import os

class Command(BaseCommand):
    help = 'Check for package security issues for npm packes.'

    def handle(self, *args, **options):
        
        ubuntu_insecure_path = str(settings.BASE_DIR) + '/db/npm_insecure/'
        ubuntu_version_path = str(settings.BASE_DIR) + '/db/npm_versions/'
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
                    # print (item_path)
                    for item2 in os.listdir(ubuntu_insecure_path+item):
                        # print (item2)
                        for item3 in os.listdir(ubuntu_insecure_path+item+'/'+item2):
                            # print (item3)
                            for item4 in os.listdir(ubuntu_insecure_path+item+'/'+item2+'/'+item3):
                                # print (item4)                            

                                opened_file = open(ubuntu_insecure_path+item+'/'+item2+'/'+item3+'/'+item4, "r")
                                insecure_full = opened_file.read()
                                insecure_full_json  = json.loads(insecure_full)
                                # print (insecure_full_json)
                                opened_file.close()
                                for i in insecure_full_json['affected']:
                                    if "package" in i:
                                        if "ecosystem" in i["package"]:
                                            if i["package"]["ecosystem"] == 'npm':
                                                
                                                npm_pack = models.NpmPackage.objects.filter(package_name=i["package"]["name"])
                                                for npm_package in npm_pack:
                                                    # print (npm_package.package_name)
                                                    package_prefix = npm_package.package_name[:2]
                                                    package_store_path = ubuntu_version_path+'/'+package_prefix                                                    
                                                    full_file_path = package_store_path+"/"+npm_package.package_name+".json"

                                                    opened_file = open(full_file_path, "r")
                                                    package_versions = opened_file.read()
                                                    # print (package_versions)
                                                    package_versions_json  = json.loads(package_versions)
                                                    # print (insecure_full_json)
                                                    opened_file.close()    
                                                    # print (i)
                                                    available_versions = []
                                                    for pv in package_versions_json:                                                                        
                                                        available_versions.append(Version(pv))


                                                                      
                                                        # print ("VUN:"+pv)
                                                    if "ranges" in i:
                                                        affected_ranges = i["ranges"] 
                                                        # print (item4)
                                                        introduced_version = ''
                                                        fixed_version = '' 
                                                        last_affected_version = ''                                                       
                                                        for ar in affected_ranges:
                                                            if "events" in ar:
                                                                affected_events = ar["events"]
                                                                
                                                                for ae in affected_events:

                                                                    if "introduced" in ae:
                                                                        introduced_version = ae["introduced"]
                                                                        print ("Introduced Version: "+introduced_version)
                                                                    if "fixed" in ae:
                                                                        fixed_version = ae["fixed"]
                                                                        print ("Fixed Version: "+fixed_version)
                                                                    if "last_affected" in ae:
                                                                        last_affected_version = ae["last_affected"]
                                                                        print ("Last Affected Version: "+last_affected_version)
                                                                    

                                                        vuln_version = False
                                                        # npm_range = NpmSpec('^'+introduced_version+' || '+fixed_version)
                                                        # npm_range = NpmSpec('^0>= <1.9.0')
                                                        # npm_range = NpmSpec('>=0 <1.9.0')
                                                        if fixed_version == '':
                                                            if last_affected_version == '':
                                                                if "database_specific" in i:
                                                                    if "last_known_affected_version_range" in i["database_specific"]:
                                                                        last_known_affected_version_range = i["database_specific"]["last_known_affected_version_range"]
                                                                        print (">="+introduced_version+" "+last_known_affected_version_range.replace(' ',''))
                                                                        npm_range = NpmSpec(">="+introduced_version+" "+last_known_affected_version_range.replace(' ',''))
                                                            else:
                                                                fixed_version = last_affected_version
                                                                print (">="+introduced_version+" <"+fixed_version)
                                                                npm_range = NpmSpec(">="+introduced_version+" <"+fixed_version)                                                                
                                                        else:
                                                            print (item4)
                                                            print (">="+introduced_version+" <"+fixed_version)
                                                            npm_range = NpmSpec(">="+introduced_version+" <"+fixed_version)
                                                        
                                                                        # if pv == introduced_version or introduced_version == '0':
                                                                        #     vuln_version = True
                                                                        # if pv == fixed_version:
                                                                        #     vuln_version = False
                                                                        
                                                                        # if vuln_version == True:
                                                                        #     print ("Fixed Version BB: "+fixed_version)
                                                                        #     if npm_package.package_name == 'jquery':

                                                                        #         print (pv)

                                                    # if introduced_version == '' and fixed_version == '':
                                                    #     if "versions" in i:
                                                    #         affected_versions= i["versions"] 
                                                    #         print (affected_versions)
                                                    #         print (item4)
                                                            
                                                    #         for pv in package_versions_json:
                                                    #             if pv in affected_versions:
                                                    #                 pass    
                                                    #                 print ("VUN2:"+pv)    
                                                            
                                                    #         npm_range = NpmSpec(">="+introduced_version+" <"+fixed_version)                                                    

                                                    for pv in package_versions_json:                                                            
                                                            if Version(pv) in npm_range:
                                                                pass
                                                                #print ("VUN:"+pv)

                                                    
                                                                if npm_pack.count() > 0:
                                                                    print ("Found Package: " + i["package"]["name"])
                                                        # for v in i["versions"]:
                                                        #      print (npm_pack[0].current_package_version)

                                                                    if npm_pack[0].current_package_version == pv:
                                                                        print ("Found Vulnerable Version: " + pv)
                                                                        ppv = None
                                                                        if models.NpmPackageVulnerability.objects.filter(package_name=i["package"]["name"]).count() > 0:
                                                                            pass
                                                                            ppv = models.NpmPackageVulnerability.objects.get(package_name=i["package"]["name"])
                                                                            #ppv.save()
                                                                        else:
                                                                            ppv = models.NpmPackageVulnerability.objects.create(package_name=i["package"]["name"])

                                                                        ppvv = None
                                                                        if models.NpmPackageVulnerabilityVersion.objects.filter(npm_package=ppv,package_version=pv).count() > 0:

                                                                            ppvv = models.NpmPackageVulnerabilityVersion.objects.get(npm_package=ppv,package_version=pv)
                                                                        else:

                                                                            ppvv = models.NpmPackageVulnerabilityVersion.objects.create(npm_package=ppv,package_version=pv)

                                                                        cve = ''
                                                                        if "aliases" in insecure_full_json:
                                                                            if len(insecure_full_json['aliases']) > 0:
                                                                                cve = insecure_full_json['aliases'][0]
                                                                                                              
                                                                        print (cve)
                                                                        advisory_info = ''
                                                                        if "details" in insecure_full_json:                                            
                                                                            advisory_info = insecure_full_json['details']                                                                                    

                                                                        ppvvai = None
                                                                        if models.NpmPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=ppvv,cve=cve).count() > 0:
                                                                            ppvvai = models.NpmPackageVulnerabilityVersionAdvisoryInformation.objects.get(package_version=ppvv,cve=cve)
                                                                        else:
                                                                            ppvvai = models.NpmPackageVulnerabilityVersionAdvisoryInformation.objects.create(package_version=ppvv,cve=cve, advisory=advisory_info)

                    #         # FOLDER
                    #         folders.append(item2)
                    # #print (folders)



        except Exception as e:
            print("An error occurred while checking for vulnerable packages:")
            print(e)
            