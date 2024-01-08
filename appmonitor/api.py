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
        checks = utils.get_checks(None)
        return HttpResponse(json.dumps(checks), content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 

@csrf_exempt
def get_checks_alerts(request, *args, **kwargs):    

    if request.user.is_authenticated:
        checks = utils.get_checks([1,2])
        return HttpResponse(json.dumps(checks), content_type='application/json', status=200)
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
        platform_obj.save()

        return HttpResponse("Successfully Updated", content_type='text/html', status=200)
    
    except Exception as e:
        print (e)
        return HttpResponse("ERROR:"+ str(e), content_type='text/html', status=500)
    print (json_data['platform_obj'])
    
    #print (request.REQUEST.get('platform_obj','{}'))

def get_platform_info(request, *args, **kwargs):    

    if request.user.is_authenticated:
        data = utils.get_platform_info()
        return HttpResponse(json.dumps(data), content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 


def get_platform_packages_info(request, *args, **kwargs):    
    search_package = request.GET.get('search_package', None)

    if request.user.is_authenticated:
        data = utils.get_platform_packages_info(search_package)
        return HttpResponse(json.dumps(data), content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 



