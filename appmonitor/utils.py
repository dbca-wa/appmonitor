import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import Group
from django.db.models import Q
from appmonitor import models
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from appmonitor import models
from pytz import timezone
from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings


def get_checks(status_types, *args, **kwargs):    
    current_time = datetime.today()
    monitors = []
    monitor = models.Monitor.objects.filter(active=True)
    monitor_status_total = {0 : 0, 1 : 0, 2 : 0, 3:0}
    monitor_status = {"last_job_run": "", "time_differnce_last_job" : "","current_time": current_time.astimezone().strftime('%d %b %Y %H:%M %p')}
    now = datetime.utcnow().replace(tzinfo=utc)
    if status_types is None:
        status_types = []
        for mh_status in models.MonitorHistory.STATUS:
            status_types.append(mh_status[0])
           


    mjl = models.MonitorJobLog.objects.all().order_by('-id').first()
    if mjl is not None:
        if mjl.started:
            timediff = now - mjl.started
            monitor_status['last_job_run'] = mjl.started.astimezone().strftime('%d %b %Y %H:%M %p')
            monitor_status['time_differnce_last_job'] = int(timediff.total_seconds() / 60)
        else:
            monitor_status['last_job_run'] = "No last run date time"
            monitor_status['time_differnce_last_job'] = 1000
    else:
        monitor_status['last_job_run'] = "No last run date time"
        monitor_status['time_differnce_last_job'] = 1000

    #Current Time: April 30, 2023, 3:18 p.m.
    
    for m in monitor:
        mh = models.MonitorHistory.objects.filter(monitor=m).order_by('-id')[:1]         
        responsible_group_name = ''
        if  m.group_responsible:
            responsible_group_name= m.group_responsible.group_name   
        if len(mh) > 0:
            monitor_status_total[mh[0].status] = monitor_status_total[mh[0].status] + 1
            created = ''
            if mh[0].created:
                created = mh[0].created.astimezone().strftime('%d/%m/%Y %H:%M %p')
            system_id_url = ''
            if settings.IT_SYSTEM_REGISTER:
                if m.system_id:
                    system_id_url = settings.IT_SYSTEM_REGISTER+'&q='+m.system_id
            if mh[0].status in status_types:
                
                monitors.append({'id': m.id, 'mon_type': m.get_mon_type_display(),'type': 'direct', 'name': m.check_name, 'status': mh[0].status,'last_check_date': created, 'active' : m.active, 'url': m.url, 'system_id': m.system_id, 'it_system_register_url': system_id_url, 'responsible_group': responsible_group_name})            
        else:
            monitor_status_total[0] = monitor_status_total[0] + 1
            monitors.append({'id': m.id, 'mon_type': m.get_mon_type_display(), 'type': 'direct', 'name': m.check_name, 'status': 0,'last_check_date': '0000-00-00', 'active' : m.active, 'url': m.url, 'system_id': m.system_id, 'it_system_register_url': settings.IT_SYSTEM_REGISTER+'&q='+m.system_id, 'responsible_group': responsible_group_name})                            
    monitors_sorted = sorted(monitors, key=lambda d: d['last_check_date'], reverse=True) 
    return {'status': 200, 'monitor_status': monitor_status, 'monitor_status_total' : monitor_status_total, 'monitors': monitors_sorted, 'message': "Data Retreived"}


def get_platform_info(*args, **kwargs):    
    
    platform_info_obj = models.Platform.objects.filter(active=True)
    platform_info_array = []
    for pi in platform_info_obj:
        row = {}
        row["id"] = pi.id
        row["system_name"] = pi.system_name
        row["operating_system_name"] = pi.operating_system_name
        row["operating_system_version"] = pi.operating_system_version
        row["python_version"] = pi.python_version
        row["django_version"] = pi.django_version
        group_responsible_id = None
        if pi.group_responsible:
            group_responsible_id = pi.group_responsible.id
        row["group_responsible_id"] = group_responsible_id
        row["group_responsible_group_name"] = pi.group_responsible.group_name
        row["updated"] = pi.updated.astimezone().strftime('%d/%m/%Y %H:%M %p')
        row["created"] = pi.created.astimezone().strftime('%d/%m/%Y %H:%M %p')
        platform_info_array.append(row)

    return {"status": 200, "platform_info_array": platform_info_array}

def get_platform_packages_info(search_package, only_vulnerable, exact_match, *args, **kwargs):    
    query_obj = Q()
    if search_package:
        if exact_match == 'true':
            query_obj = Q(package_name=search_package,active=True) | Q(current_package_version=search_package)
        else:
            query_obj = Q(package_name__icontains=search_package,active=True) | Q(current_package_version__icontains=search_package)
    else:
        query_obj = Q(active=True)  
    
    if only_vulnerable == 'true':
        query_obj &= Q(vulnerability_total__gt=0)

    platform_packages_info_obj = models.PythonPackage.objects.filter(query_obj)
    platform_packages_info_array = []
    for ppi in platform_packages_info_obj:
        row = {}
        row["id"] = ppi.id
        row['package_name'] = ppi.package_name
        row['current_package_version'] = ppi.current_package_version
        row['vulnerability_total'] = ppi.vulnerability_total
        row['active'] = ppi.active
        row['updated'] = ppi.updated.astimezone().strftime('%d/%m/%Y %H:%M %p')
        row['created'] =  ppi.created.astimezone().strftime('%d/%m/%Y %H:%M %p')
        row["platform_id"] = ppi.platform.id
        row["system_name"] = ppi.platform.system_name
        row["operating_system_name"] = ppi.platform.operating_system_name
        row["operating_system_version"] = ppi.platform.operating_system_version
        row["python_version"] = ppi.platform.python_version
        row["django_version"] = ppi.platform.django_version
        row["group_responsible_id"] = ppi.platform.group_responsible.id
        row["group_responsible_group_name"] = ppi.platform.group_responsible.group_name
        row["platform_updated"] = ppi.platform.updated.astimezone().strftime('%d/%m/%Y %H:%M %p')
        row["platform_created"] = ppi.platform.created.astimezone().strftime('%d/%m/%Y %H:%M %p')
        platform_packages_info_array.append(row)

    return {"status": 200, "platform_packages_info_array": platform_packages_info_array}

def get_vul_specs(vun_specs):
    #print (vun_specs)
    vun_specs_split = vun_specs.split(",")

    check_type = ""
    from_operator = ""
    from_version = ""
    to_operator = ""
    to_version = ""

    if len(vun_specs_split) == 1:
        check_type = "single"
        gopv = get_operator_plus_version(vun_specs_split[0])
        from_operator = gopv['operator']
        from_version = gopv['version']
    elif len(vun_specs_split) == 2:
        check_type = "double"
        gopv = get_operator_plus_version(vun_specs_split[0])
        from_operator = gopv['operator']
        from_version = gopv['version']
        gopv = get_operator_plus_version(vun_specs_split[1])
        to_operator = gopv['operator']
        to_version = gopv['version']

    else:
        print ('No vulnerability to match')
    return {"check_type": check_type, "from_operator": from_operator, "from_version": from_version, "to_operator": to_operator, "to_version": to_version}


def get_operator_plus_version(vun):
    if vun[0:2] in ['==', '>=' , '<=']:
        # double char operator
        operator = vun[0:2]
        version = vun[2:len(vun)]
    else:
        if vun[0:1] in ['<', '>']:
            # single char operator
            operator = vun[0:1]
            version = vun[1:len(vun)]
        else:
            # unable to determine operator
            print ("unable to determine operator")

    return {"operator": operator, "version": version}


