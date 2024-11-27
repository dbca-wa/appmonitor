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

class Command(BaseCommand):
    help = 'Check for package security issues.'

    def handle(self, *args, **options):
        
        error_row = []
        try:
            f = open(str(settings.BASE_DIR)+'/db/insecure_full.json', "r")
            insecure_full = f.read()
            insecure_full_json  = json.loads(insecure_full)
            
            python_pacakges_obj = models.PythonPackage.objects.all().values_list('package_name', flat=True).distinct()
            total_package_count = python_pacakges_obj.count()
            start_package_count = 0
            for pp in python_pacakges_obj:
                print (pp)
                start_package_count = start_package_count + 1
                print ("ROLLING COUNT: "+str(start_package_count)+":"+str(total_package_count))
                if pp in insecure_full_json:
                    
                    package_insecure_information = insecure_full_json[pp]
                    #Save Data
                    ppv = None
                    if models.PythonPackageVulnerability.objects.filter(package_name=pp).count() > 0:
                        ppv = models.PythonPackageVulnerability.objects.get(package_name=pp)
                        ppv.vulnerability_json = package_insecure_information
                        ppv.save()
                    else:
                        ppv = models.PythonPackageVulnerability.objects.create(package_name=pp,
                                                                                vulnerability_json=package_insecure_information
                                                                                )                       
                    for insecure in package_insecure_information:
                        specs_vul = insecure['specs']

                        # package information url https://pypi.org/pypi/django/json
                        package_versions = []
                        package_versions_slim = []
                        f = open(str(settings.BASE_DIR)+'/python_packages_db/'+pp[0:1]+'/'+pp[1:2]+'/'+pp+'.json', "r")
                        package_info = f.read()
                        package_info_json  = json.loads(package_info)

                        for r in package_info_json['releases']:
                            if len(package_info_json['releases'][r]) > 0:
                                package_versions.append(r)
                            
                        try:
                            package_versions.sort(key=parseVersion)
                        except Exception as e:
                            error_row.append(pp+" with error "+str(e))
                            print (e)
                        
                        list_of_vulnerable_packages = []
                        try: 
                            for sv in specs_vul:
                                gvs = utils.get_vul_specs(sv)
                                if gvs["check_type"] == 'single':
                                    if gvs["from_version"] not in package_versions:
                                        print ("This version "+gvs["from_version"]+" is not listed for this package")
                                        continue

                                    if gvs["from_operator"] == '>':
                                        # will need to assess this when data permit.  Logically everything with single check_type should be negative.
                                        pass
                                    if gvs["from_operator"] == '==':
                                        for r in package_versions:
                                            if r == gvs["from_version"]:
                                                list_of_vulnerable_packages.append(r)

                                    if gvs["from_operator"] == '<':
                                        
                                        for r in package_versions:
                                            if r == gvs["from_version"]:
                                                break
                                            list_of_vulnerable_packages.append(r)

                                if gvs["check_type"] == 'double':
                                    
                                    if gvs["from_version"] not in package_versions:
                                        print ("This version "+gvs["from_version"]+" is not listed for this package")
                                        continue
                                    if gvs["to_version"] not in package_versions:
                                        print ("This version "+gvs["to_version"]+" is not listed for this package")
                                        continue

                                    vul_version = False
                                    for r in package_versions:

                                        #equal opertors occur before vul_version is set to true(if no equal then set vul_version true after array append)
                                        if gvs["from_operator"] == '>=':
                                            if gvs["from_version"] == r:
                                                vul_version = True

                                        if gvs["to_operator"] == '<':
                                            
                                            if gvs["to_version"] == r:
                                                vul_version = False   

                                        if vul_version is True:
                                        
                                            list_of_vulnerable_packages.append(r)           

                                        if gvs["from_operator"] == '>':
                                            if gvs["from_version"] == r:
                                                vul_version = True
                                        if gvs["to_operator"] == '<=':
                                            if gvs["to_version"] == r:
                                                vul_version = False 
                        except Exception as e:
                            error_row.append(pp+" with error "+str(e))
                            print (e)      
                        
                        print (list_of_vulnerable_packages)          

                        for lovp in list_of_vulnerable_packages:
                            ppvv = None
                            if models.PythonPackageVulnerabilityVersion.objects.filter(python_package=ppv,package_version=lovp).count() > 0:
                                ppvv = models.PythonPackageVulnerabilityVersion.objects.get(python_package=ppv, package_version=lovp)
                            else:
                                ppvv = models.PythonPackageVulnerabilityVersion.objects.create(python_package=ppv, package_version=lovp)
                            ####                                                           
                            ppvvai = None
                            if models.PythonPackageVulnerabilityVersionAdvisoryInformation.objects.filter(package_version=ppvv,cve=insecure['cve']).count() > 0:
                                ppvvai = models.PythonPackageVulnerabilityVersionAdvisoryInformation.objects.get(package_version=ppvv,cve=insecure['cve'])
                            else:
                                ppvvai = models.PythonPackageVulnerabilityVersionAdvisoryInformation.objects.create(package_version=ppvv,cve=insecure['cve'], advisory=insecure['advisory'])


            # 
            if total_package_count != start_package_count:
                error_row.append(" Rolling row count is {} : {} ".format(start_package_count,total_package_count))

            if len(error_row) > 0:
                t = email_templates.SystemError()
                t.subject = "App monitor system errors in check_for_vulnerable_packages"
                to_addresses=[settings.NOTIFICATION_EMAIL]
                
                print ("Preparing to email: "+str(to_addresses))
                t.send(to_addresses=to_addresses, context={"settings": settings, 'system_errors': error_row})



        except Exception as e:
            print (e)