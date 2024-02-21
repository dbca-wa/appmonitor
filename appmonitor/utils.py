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


def get_checks(status_types, filters, *args, **kwargs):    
    current_time = datetime.today()
    monitors = []
    filters_query = Q()
    if filters:
    
        active = True
        if filters['responsiblegroup'] == '':
            filters['responsiblegroup'] = 0
        if filters['inactive'] == 'true' or filters['inactive'] is True:        
            active = False

        if filters['responsiblegroup']:
            if int(filters['responsiblegroup']) > 0:
                filters_query &= Q(group_responsible=int(filters['responsiblegroup']))
        if active is True:
            filters_query &= Q(active=True)

        if filters['keyword']:            
            if len(filters['keyword']) > 2: 
                filters_query &= Q(check_name__icontains=filters['keyword'])

        monitor = models.Monitor.objects.filter(filters_query)  
    else:
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
            
            if m.system_id is None:
                system_id = ''
            else:
                system_id = m.system_id

            monitor_status_total[0] = monitor_status_total[0] + 1
            monitors.append({'id': m.id, 'mon_type': m.get_mon_type_display(), 'type': 'direct', 'name': m.check_name, 'status': 0,'last_check_date': '0000-00-00', 'active' : m.active, 'url': m.url, 'system_id': system_id, 'it_system_register_url': settings.IT_SYSTEM_REGISTER+'&q='+system_id, 'responsible_group': responsible_group_name})                            
    monitors_sorted = sorted(monitors, key=lambda d: d['last_check_date'], reverse=True) 
    return {'status': 200, 'monitor_status': monitor_status, 'monitor_status_total' : monitor_status_total, 'monitors': monitors_sorted, 'message': "Data Retreived"}


def get_platform_info(pid, filters=None, *args, **kwargs):    
    
    if pid is None:
        
        filters_query = Q()
        if filters:
        
            active = True
            if filters['responsiblegroup'] is None:
               filters['responsiblegroup'] = 0 
            if filters['responsiblegroup'] == '':
                filters['responsiblegroup'] = 0
            if filters['inactive'] == 'true' or filters['inactive'] is True:        
                active = False

            if int(filters['responsiblegroup']) > 0:
                filters_query &= Q(group_responsible=int(filters['responsiblegroup']))
            if active is True:
                filters_query &= Q(active=True)
                
            if len(filters['keyword']) > 2: 
                filters_query &= Q(system_name__icontains=filters['keyword'])
            platform_info_obj = models.Platform.objects.filter(filters_query)
             
        else:
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
            row['vulnerability_total'] = pi.vulnerability_total
            group_responsible_id = None
            group_responsible_name = None
            if pi.group_responsible:
                group_responsible_id = pi.group_responsible.id
                group_responsible_name = pi.group_responsible.group_name
            row["group_responsible_id"] = group_responsible_id
            row["group_responsible_group_name"] = group_responsible_name
            row["updated"] = pi.updated.astimezone().strftime('%d/%m/%Y %H:%M %p')
            row["created"] = pi.created.astimezone().strftime('%d/%m/%Y %H:%M %p')
            last_sync_dt = 'No Sync'
            if pi.last_sync_dt:
                last_sync_dt = pi.last_sync_dt.astimezone().strftime('%d/%m/%Y %H:%M %p')
            row["last_sync_dt"] = last_sync_dt
            platform_info_array.append(row)
        return {"status": 200, "platform_info_array": platform_info_array}
    else:
        pi = platform_info_obj = models.Platform.objects.get(id=pid)

        row = {}
        row["id"] = pi.id
        row["system_name"] = pi.system_name
        row["api_key"] = pi.api_key
        row['stale_packages'] = pi.stale_packages
        row['active'] = pi.active
        row["operating_system_name"] = pi.operating_system_name
        row["operating_system_version"] = pi.operating_system_version
        row["python_version"] = pi.python_version
        row["django_version"] = pi.django_version
        group_responsible_id = None
        group_responsible_name = None
        if pi.group_responsible:
            group_responsible_id = pi.group_responsible.id
            group_responsible_name = pi.group_responsible.group_name
        row["group_responsible_id"] = group_responsible_id
        row["group_responsible_group_name"] = group_responsible_name
        row["updated"] = pi.updated.astimezone().strftime('%d/%m/%Y %H:%M %p')
        row["created"] = pi.created.astimezone().strftime('%d/%m/%Y %H:%M %p')
        last_sync_dt = 'No Sync'
        if pi.last_sync_dt:
            last_sync_dt = pi.last_sync_dt.astimezone().strftime('%d/%m/%Y %H:%M %p')
        row["last_sync_dt"] = last_sync_dt
        return {"status": 200, "platform_info_array": row}

def get_monitor_info(mid, *args, **kwargs): 
        mo = monitor_info_obj = models.Monitor.objects.get(id=mid)
        row = {}
        row["id"] = mo.id
        row["check_name"] = mo.check_name
        row["mon_type"] = mo.mon_type   
        row['check_operator'] = mo.check_operator
        row['system_id'] = mo.system_id

        group_responsible_id = None
        group_responsible_name = None
        if mo.group_responsible:
            group_responsible_id = mo.group_responsible.id
            group_responsible_name = mo.group_responsible.group_name

        row["group_responsible_id"] = group_responsible_id
        row["group_responsible_group_name"] = group_responsible_name
        row["url"] = mo.url
        row["string_check"] = mo.string_check
        row["json_key"] = mo.json_key
        row["status_code"] = mo.status_code
        row["host"] = mo.host
        row["port"] = mo.port
        row["ignore_ssl_verification"] = mo.ignore_ssl_verification
        
        row["use_basic_auth"] = mo.use_basic_auth
        row["username"] = mo.username
        row["password"] = mo.password

        row["sharepoint_url"] = mo.sharepoint_url
        row["sharepoint_username"] = mo.sharepoint_username
        row["sharepoint_password"] = mo.sharepoint_password        

        row["db_type"] = mo.db_type
        row["db_host"] = mo.db_host
        row["db_name"] = mo.db_name
        row["db_username"] = mo.db_username
        row["db_password"] = mo.db_password
        row["db_port"] = mo.db_port
        row["db_query"] = mo.db_query

        row["up_value"] = mo.up_value
        row["warn_value"] = mo.warn_value
        row["down_value"] = mo.down_value
        row["active"] = mo.active

        # row["updated"] = mo.updated.astimezone().strftime('%d/%m/%Y %H:%M %p')
        # row["created"] = mo.created.astimezone().strftime('%d/%m/%Y %H:%M %p')
        return {"status": 200, "monitor_info_array": row}    

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


def user_group_permissions(request):
    view_monitor_status_access = False
    edit_platform_access = False
    view_access_platform_status = False
    view_access_package_status = False
    edit_access_monitoring = False

    # Get acccess riles
    view_access_groups = models.AccessGroup.objects.filter(active=True, access_type=1)
    view_access_groups_array = []
    for vag in view_access_groups:
        view_access_groups_array.append(vag.group_name)

    edit_access_groups = models.AccessGroup.objects.filter(active=True, access_type=2)
    edit_access_groups_array = []
    for eag in edit_access_groups:
        edit_access_groups_array.append(eag.group_name)

    view_access_platform_status_groups = models.AccessGroup.objects.filter(active=True, access_type=3)
    view_access_platform_status_array = []
    for eag in view_access_platform_status_groups:
        view_access_platform_status_array.append(eag.group_name)
    
    view_access_package_status_groups = models.AccessGroup.objects.filter(active=True, access_type=4)
    view_access_package_status_array = []
    for eag in view_access_package_status_groups:
        view_access_package_status_array.append(eag.group_name)

    edit_access_monitoring_groups = models.AccessGroup.objects.filter(active=True, access_type=5)
    edit_access_monitoring_array = []
    for eag in edit_access_monitoring_groups:
        edit_access_monitoring_array.append(eag.group_name)


    user_groups = []
    for g in request.user.groups.all():
        user_groups.append(g.name)
    
    for ug in user_groups:
        if ug in view_access_groups_array:
            view_monitor_status_access = True

    for ug in user_groups:
        if ug in edit_access_groups_array:
            edit_platform_access = True

    for ug in user_groups:
        if ug in view_access_platform_status_array:
            view_access_platform_status = True            

    for ug in user_groups:
        if ug in view_access_package_status_array:
            view_access_package_status = True      

    for ug in user_groups:
        if ug in edit_access_monitoring_array:
            edit_access_monitoring = True     

    access_type = {
        'view_monitor_status_access' : view_monitor_status_access,
        'edit_platform_access' : edit_platform_access,
        'view_access_platform_status' : view_access_platform_status,
        'view_access_package_status' : view_access_package_status,
        'edit_access_monitoring' : edit_access_monitoring
    }
    
    return access_type