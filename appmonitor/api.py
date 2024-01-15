import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import Group
from django.db.models import Q
from appmonitor import models
from appmonitor import utils
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from appmonitor import models
from pytz import timezone
from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings


@csrf_exempt
def get_checks(request, *args, **kwargs):    

    if request.user.is_authenticated:
        access_type = utils.user_group_permissions(request)
        if access_type['view_monitor_status_access'] is True:   
            checks = utils.get_checks(None)
            return HttpResponse(json.dumps(checks), content_type='application/json', status=200)
        else:
            return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403)         
        
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 

@csrf_exempt
def get_checks_alerts(request, *args, **kwargs):    

    if request.user.is_authenticated:
        access_type = utils.user_group_permissions(request)
        if access_type['view_monitor_status_access'] is True:          
            checks = utils.get_checks([1,2])
            return HttpResponse(json.dumps(checks), content_type='application/json', status=200)
        else:
            return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403)            
    
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 

@csrf_exempt
def update_platform_information(request, *args, **kwargs):

    try:
        json_body = request.body.decode()
        json_data = json.loads(json_body)
        APP_MONITOR_PLATFORM_ID = json_data['APP_MONITOR_PLATFORM_ID']
        print ("Updating Platform Information for ID: {}".format(APP_MONITOR_PLATFORM_ID))
        APP_MONITOR_APIKEY = json_data['APP_MONITOR_APIKEY']
        platform_obj = models.Platform.objects.get(id=APP_MONITOR_PLATFORM_ID,api_key=APP_MONITOR_APIKEY)
        platform_obj.operating_system_name = json_data['platform_obj']['system_info']['NAME']
        platform_obj.operating_system_version = json_data['platform_obj']['system_info']['VERSION_ID']
        platform_obj.python_version = json_data['platform_obj']['system_info']['python_version']
        platform_obj.django_version = json_data['platform_obj']['system_info']['django_version']
        platform_obj.json_response = json_data
        platform_obj.stale_packages = True
        platform_obj.last_sync_dt = datetime.now()
        platform_obj.save()

        return HttpResponse("Successfully Updated", content_type='text/html', status=200)
    
    except Exception as e:
        print (e)
        return HttpResponse("ERROR:"+ str(e), content_type='text/html', status=500)
    
    
    #print (request.REQUEST.get('platform_obj','{}'))

def platform_create(request, *args, **kwargs):  
    
    if request.user.is_authenticated:
        try:
            access_type = utils.user_group_permissions(request)
            if access_type['edit_platform_access'] is True:
                json_body = json.loads(request.body.decode())
                

                responsiblegroup = models.ResponsibleGroup.objects.get(id=json_body['platform_responsiblegroup'])
                models.Platform.objects.create(system_name=json_body['platform_systemname'], api_key=json_body['platform_apikey'],group_responsible=responsiblegroup,stale_packages=json_body['platform_stalepackage'],active=json_body['platform_active'])


                #json_body['platform_stalepackage']
                data = {"working": "working"}
                
                return HttpResponse(json.dumps(data), content_type='application/json', status=200)
            else:
                return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 
        except Exception as e:

            print (e)
            return HttpResponse("ERROR:"+ str(e), content_type='text/html', status=500)    

    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 

def platform_update(request, *args, **kwargs):  
    if request.user.is_authenticated:
        try:
            access_type = utils.user_group_permissions(request)
            if access_type['edit_platform_access'] is True:            
                json_body = json.loads(request.body.decode())
                print (json_body)

                responsiblegroup = models.ResponsibleGroup.objects.get(id=json_body['platform_responsiblegroup'])
                platform = models.Platform.objects.get(id=json_body['platform_id'])
                platform.system_name =json_body['platform_systemname']
                platform.api_key = json_body['platform_apikey']
                platform.group_responsible =responsiblegroup
                platform.stale_packages = json_body['platform_stalepackage']
                platform.active = json_body['platform_active']
                platform.save()

                #json_body['platform_stalepackage']
                data = {"working": "working"}
                
                return HttpResponse(json.dumps(data), content_type='application/json', status=200)
            else:
                return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403)             
        except Exception as e:

            print (e)
            return HttpResponse("ERROR:"+ str(e), content_type='text/html', status=500)    

    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 
    
def get_platform_info(request, *args, **kwargs):    

    if request.user.is_authenticated:
        access_type = utils.user_group_permissions(request)
        if access_type['view_access_platform_status'] is True:           
            data = utils.get_platform_info(None)        
            return HttpResponse(json.dumps(data), content_type='application/json', status=200)
        else:
            return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403)      
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 

def get_platform_info_by_id(request, *args, **kwargs):    

    if request.user.is_authenticated:
        data = {}
        try:
            access_type = utils.user_group_permissions(request)
            if access_type['view_access_platform_status'] is True:                                
                pid = kwargs['pk']
                #pid = request.GET.get('pid',None)
                if pid:
                    data = utils.get_platform_info(pid)
                else:
                    return HttpResponse(json.dumps({'status': 404, 'message': "No PID data"}), content_type='application/json', status=403)  
                return HttpResponse(json.dumps(data), content_type='application/json', status=200)
            else:
                return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403)                
        except Exception as e:
            print (e)
            return HttpResponse(json.dumps({'status': 500, 'message': str(e)}), content_type='application/json', status=403) 
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 


def get_platform_packages_info(request, *args, **kwargs):    
    search_package = request.GET.get('search_package', None)
    only_vulnerable = request.GET.get('only_vulnerable', False)
    exact_match = request.GET.get('exact_match', False)

    if request.user.is_authenticated:
        data = utils.get_platform_packages_info(search_package, only_vulnerable, exact_match)
        return HttpResponse(json.dumps(data), content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 

def monitoring_create(request, *args, **kwargs):  
    
    if request.user.is_authenticated:
        try:
            access_type = utils.user_group_permissions(request)
            if access_type['edit_access_monitoring'] is True:
                json_body = json.loads(request.body.decode())
                print (json_body)
                check_operator = None
                if len(json_body['operator']) == 0:
                    pass
                else:
                    check_operator = json_body['operator']

                status_code = None
                if json_body['statuscode'].isnumeric() > 0:
                    status_code = int(json_body['statuscode'])
                
                    
                
                responsiblegroup = models.ResponsibleGroup.objects.get(id=json_body['responsiblegroup'])
                models.Monitor.objects.create(
                                                check_name = json_body['checkname'],
                                                mon_type = json_body['montype'],
                                                check_operator = check_operator,
                                                system_id = json_body['systemid'],
                                                group_responsible =  responsiblegroup,                                                
                                                url = json_body['url'],
                                                string_check = json_body['stringcheck'],
                                                json_key = json_body['jsonkey'],
                                                status_code = status_code,
                                                host = json_body['host'],
                                                port = json_body['port'],
                                                ignore_ssl_verification = json_body['ignoressl'],                                                                                                
                                                use_basic_auth = json_body['basicauth'],
                                                username = json_body['username'],
                                                password = json_body['password'],
                                                sharepoint_url = json_body['sharepointurl'],
                                                sharepoint_username = json_body['sharepointusername'],
                                                sharepoint_password = json_body['sharepointpassword'],
                                                up_value = json_body['up'],
                                                warn_value = json_body['warn'],
                                                down_value = json_body['down'],
                                                active = json_body['active']
                )                
                data = {'working': 'working'}
                return HttpResponse(json.dumps(data), content_type='application/json', status=200)
            else:
                return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 
        except Exception as e:

            print (e)
            return HttpResponse("ERROR:"+ str(e), content_type='text/html', status=500)    

    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 

def monitoring_update(request, *args, **kwargs):  
    if request.user.is_authenticated:
        try:
            access_type = utils.user_group_permissions(request)
            if access_type['edit_access_monitoring'] is True:            
                json_body = json.loads(request.body.decode())
                print (json_body)
                check_operator = None
                if len(json_body['operator']) == 0:
                    pass
                else:
                    check_operator = json_body['operator']

                status_code = None
                if json_body['statuscode'].isnumeric() > 0:
                    status_code = int(json_body['statuscode'])
               
                responsiblegroup = models.ResponsibleGroup.objects.get(id=json_body['responsiblegroup'])                
                monitor = models.Monitor.objects.get(id=json_body['monitor_id'])
                monitor.check_name = json_body['checkname']
                monitor.mon_type = json_body['montype']
                monitor.check_operator = check_operator
                monitor.system_id = json_body['systemid']
                monitor.group_responsible =  responsiblegroup                                              
                monitor.url = json_body['url']
                monitor.string_check = json_body['stringcheck']
                monitor.json_key = json_body['jsonkey']
                monitor.status_code = status_code
                monitor.host = json_body['host']
                monitor.port = json_body['port']
                monitor.ignore_ssl_verification = json_body['ignoressl']                                                                                                
                monitor.use_basic_auth = json_body['basicauth']
                monitor.username = json_body['username']
                monitor.password = json_body['password']
                monitor.sharepoint_url = json_body['sharepointurl']
                monitor.sharepoint_username = json_body['sharepointusername']
                monitor.sharepoint_password = json_body['sharepointpassword']
                monitor.up_value = json_body['up']
                monitor.warn_value = json_body['warn']
                monitor.down_value = json_body['down']
                monitor.active = json_body['active']
                monitor.save()

                #json_body['platform_stalepackage']
                data = {"working": "working"}
                
                return HttpResponse(json.dumps(data), content_type='application/json', status=200)
            else:
                return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403)             
        except Exception as e:

            print (e)
            return HttpResponse("ERROR:"+ str(e), content_type='text/html', status=500)    

    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 
    

def get_monitor_info_by_id(request, *args, **kwargs):

    if request.user.is_authenticated:
        data = {}
        try:
            access_type = utils.user_group_permissions(request)
            if access_type['edit_access_monitoring'] is True:                                
                pid = kwargs['pk']
                #pid = request.GET.get('pid',None)
                if pid:
                    data = utils.get_monitor_info(pid)
                else:
                    return HttpResponse(json.dumps({'status': 404, 'message': "No MID data"}), content_type='application/json', status=403)  
                return HttpResponse(json.dumps(data), content_type='application/json', status=200)
            else:
                return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403)                
        except Exception as e:
            print (e)
            return HttpResponse(json.dumps({'status': 500, 'message': str(e)}), content_type='application/json', status=403) 
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 
