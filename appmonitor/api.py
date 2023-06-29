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
        # current_time = datetime.today()
        # monitors = []
        # monitor = models.Monitor.objects.filter(active=True)
        # monitor_status_total = {0 : 0, 1 : 0, 2 : 0, 3:0}
        # monitor_status = {"last_job_run": "", "time_differnce_last_job" : "","current_time": current_time.astimezone().strftime('%d %b %Y %H:%M %p')}
        # now = datetime.utcnow().replace(tzinfo=utc)
       
        # mjl = models.MonitorJobLog.objects.all().order_by('-id').first()
        # if mjl is not None:
        #     if mjl.started:
        #         timediff = now - mjl.started
        #         monitor_status['last_job_run'] = mjl.started.astimezone().strftime('%d %b %Y %H:%M %p')
        #         monitor_status['time_differnce_last_job'] = int(timediff.total_seconds() / 60)
        #     else:
        #         monitor_status['last_job_run'] = "No last run date time"
        #         monitor_status['time_differnce_last_job'] = 1000
        # else:
        #     monitor_status['last_job_run'] = "No last run date time"
        #     monitor_status['time_differnce_last_job'] = 1000

        # #Current Time: April 30, 2023, 3:18 p.m.
        
        # for m in monitor:
        #     mh = models.MonitorHistory.objects.filter(monitor=m).order_by('-id')[:1]         
        #     responsible_group_name = ''
        #     if  m.group_responsible:
        #         responsible_group_name= m.group_responsible.group_name   
        #     if len(mh) > 0:
        #         monitor_status_total[mh[0].status] = monitor_status_total[mh[0].status] + 1
        #         created = ''
        #         if mh[0].created:
        #             created = mh[0].created.astimezone().strftime('%d/%m/%Y %H:%M %p')
        #         system_id_url = ''
        #         if settings.IT_SYSTEM_REGISTER:
        #             if m.system_id:
        #                 system_id_url = settings.IT_SYSTEM_REGISTER+'&q='+m.system_id

        #         monitors.append({'id': m.id, 'mon_type': m.get_mon_type_display(),'type': 'direct', 'name': m.check_name, 'status': mh[0].status,'last_check_date': created, 'active' : m.active, 'url': m.url, 'system_id': m.system_id, 'it_system_register_url': system_id_url, 'responsible_group': responsible_group_name})            
        #     else:
        #         monitor_status_total[0] = monitor_status_total[0] + 1
        #         monitors.append({'id': m.id, 'mon_type': m.get_mon_type_display(), 'type': 'direct', 'name': m.check_name, 'status': 0,'last_check_date': '0000-00-00', 'active' : m.active, 'url': m.url, 'system_id': m.system_id, 'it_system_register_url': settings.IT_SYSTEM_REGISTER+'&q='+m.system_id, 'responsible_group': responsible_group_name})                            
        # monitors_sorted = sorted(monitors, key=lambda d: d['last_check_date'], reverse=True) 
        checks = utils.get_checks()

        return HttpResponse(json.dumps(checks), content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps({'status': 403, 'message': "Forbidden Authentication"}), content_type='application/json', status=403) 



