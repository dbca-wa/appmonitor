from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
import datetime
from appmonitor import models

class Command(BaseCommand):
    help = 'Remove old logs.'

    def handle(self, *args, **options):
        
        try:
            platform_obj = models.Platform.objects.filter(stale_packages=True)           

            for p in platform_obj:
                platform_json = p.json_response
                vulnerability_total_count = 0   
                platform_current_severity = ""     
                if platform_json is not None:
                    if 'platform_obj' in platform_json:
                        models.PythonPackage.objects.filter(platform=p).update(active=False)
                        if 'python_packages' in platform_json['platform_obj']:           
                            python_packages = platform_json['platform_obj']['python_packages']
                            
                            for pp in python_packages:
                                print (pp)
                                package_split = pp.split('==')
                                package_name = package_split[0]
                                package_version = package_split[1]
                                python_package_obj_model = None
                                try:

                                    python_package_obj_model = models.PythonPackage.objects.get(platform=p, package_name=package_name)                                    
                                    vulnerability_total_count = vulnerability_total_count + python_package_obj_model.vulnerability_total
                                    # platform_current_severity = python_package_obj_model.severity_rollup                                   
                                    python_package_obj_model.current_package_version = package_version
                                    python_package_obj_model.active =True
                                    python_package_obj_model.save()

                                    if python_package_obj_model.severity_rollup == 'LOW':         
                                        if platform_current_severity == "MEDIUM" or platform_current_severity == "HIGH" or platform_current_severity == "CRITICAL":
                                            pass
                                        else:
                                            platform_current_severity = python_package_obj_model.severity_rollup                                                   
                                    if python_package_obj_model.severity_rollup == 'MEDIUM':
                                        if platform_current_severity == "HIGH" or platform_current_severity == "CRITICAL":
                                            pass
                                        else:
                                            platform_current_severity = python_package_obj_model.severity_rollup
                                    if python_package_obj_model.severity_rollup == 'HIGH':
                                        if platform_current_severity == "CRITICAL":
                                            pass
                                        else:
                                            platform_current_severity = python_package_obj_model.severity_rollup
                                    if python_package_obj_model.severity_rollup == 'CRITICAL':                            
                                        platform_current_severity = python_package_obj_model.severity_rollup                   


                                except Exception as e:
                                    print ("EXCEPTION1:")
                                    print (e)
                                    python_package_obj_model = models.PythonPackage.objects.create(package_name=package_name,current_package_version=package_version, platform=p, active=True)
                                
                                # create version history of package that links to the system.
                                try: 
                                    ppvh = models.PythonPackageVersionHistory.objects.get(python_package=python_package_obj_model, package_version=package_version)
                                except Exception as e:
                                    print (e)
                                    ppvh= models.PythonPackageVersionHistory.objects.create(python_package=python_package_obj_model, package_version=package_version)
                                                                
                                print (package_name)
                                print (package_version)

                    if 'debian_packages' in platform_json['platform_obj']:           
                        debian_packages = platform_json['platform_obj']['debian_packages']
                        for dp in debian_packages:                           
                            package_name = dp['package_name']
                            package_version = dp['package_version']
                            python_package_obj_model = None 
                            # print (package_name)                       
                            try:                      
                                python_package_obj_model = models.DebianPackage.objects.get(platform=p, package_name=package_name)                                    
                                vulnerability_total_count = vulnerability_total_count + python_package_obj_model.vulnerability_total
                                python_package_obj_model.current_package_version = package_version
                                python_package_obj_model.active =True
                                python_package_obj_model.save()
            
                            except Exception as e:
                                print ("EXCEPTION1:")
                                print (e)
                                python_package_obj_model = models.DebianPackage.objects.create(package_name=package_name,current_package_version=package_version, platform=p, active=True)
                        
                    models.Platform.objects.filter(id=p.id).update(stale_packages=False,vulnerability_total=vulnerability_total_count, platform_current_severity=platform_current_severity)        

        except Exception as e:
            print ("EXCEPTION2:")
            print (e)