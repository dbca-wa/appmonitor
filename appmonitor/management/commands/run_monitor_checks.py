from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from datetime import datetime as dt_datetime
from platform   import system as system_name  # Returns the system/OS name
from subprocess import call   as system_call, DEVNULL, STDOUT  # Execute a shell command
from requests.auth import HTTPBasicAuth

from urllib.request import Request, urlopen, ssl, socket
from urllib.error import URLError, HTTPError
import json

import subprocess, platform
import requests
import socket
import threading
import datetime
import json
import re

from appmonitor import models

class Command(BaseCommand):
    help = 'Run monitoring checks'
    def handle(self, *args, **options):
        mjl = models.MonitorJobLog.objects.create(job='run_monitor_checks.py')

        monitor = models.Monitor.objects.filter(active=True)
        for i in monitor:
            print ("Running checks for: "+i.check_name)

            if i.mon_type == 1:
                 thread = threading.Thread(target=self.get_website, args=(i,i.url,i.string_check))                 
                 thread.start()

            if i.mon_type == 5:
                  thread = threading.Thread(target=self.get_ssl_expiry, args=(i,i.host,int(i.port),))
                  thread.start()

        #thread still keep running not accurate finished time.  work in progress                  
        #mjl.finished = datetime.datetime.today()
        #mjl.save()

    def get_website(self, monitor,website,string_check):      
        print (monitor.check_name)
        response = None
        html_str = ''
        cookies={}
        if monitor.use_auth2_token is True:
            print (settings.AUTH2_TOKEN_URL)
            try:
                auth=auth=HTTPBasicAuth(settings.AUTH2_USERNAME,settings.AUTH2_PASSWORD)
                auth_response = requests.get(settings.AUTH2_TOKEN_URL, auth=auth)                
                print (auth_response)
                cookies = auth_response.cookies.get_dict()
                print (cookies['sessionid'])
            except Exception as e:
                print (e)


        try:
            response = requests.get(website, timeout=30, cookies=cookies)       
            print (response.text)     
        except Exception as e:
            print (e)
            html_str = str(e)
            response = None
            pass

        
        if response:
           html_str = response.text

        if string_check is None:
           string_check = ''

        if len(string_check) > 0:
           if string_check in html_str:
              self.create_monitor_history(monitor,3,'string found', html_str)
           else:
              self.create_monitor_history(monitor,1,'string not found',html_str)
        else:
           if '-!STATUSCHECK!-' in html_str:
              self.create_monitor_history(monitor,3,'string found',html_str)
           else:
              self.create_monitor_history(monitor,1,'string not found',html_str)

        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()


    def get_ssl_expiry(self,monitor,host,port):

         if port ==0:
            port = '443'
         hostname = host
         context = ssl.create_default_context()
         data = None
         try:
             with socket.create_connection((hostname, port)) as sock:
                 try:
                     with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        #print(ssock.version())
                        data = ssock.getpeercert()
                 except Exception as e:
                     print (e)
                     pass
                 # print(ssock.getpeercert())
         except Exception as e:
                pass

         if data is None:
            self.create_monitor_history(monitor,1,'Certificate Error', None)
         else:

            from datetime import datetime
            a = datetime.now()
            d= datetime.strptime(data['notAfter'], '%b %d %H:%M:%S %Y %Z')
            k = (d-a).total_seconds()
            seconds = k
            if int(seconds) > 259200:
                self.create_monitor_history(monitor,3,'Certificate OK - '+str(data['notAfter'])+' seconds:'+str(seconds), json.dumps(data))
            elif int(seconds) > 0:
                self.create_monitor_history(monitor,2,'Certificate Requires Renewal -'+str(data['notAfter'])+' seconds:'+str(seconds), json.dumps(data))
            else:
                self.create_monitor_history(monitor,1,'Certificate Expired', data['notAfter'], json.dumps(data))
         a = dt_datetime.now()
         monitor.last_update =a
         monitor.save()



    def create_monitor_history(self,monitor,status,response, response_raw):
        latest_check_status = -1
        if models.MonitorHistory.objects.filter(monitor=monitor).exists():
            latest_check = models.MonitorHistory.objects.filter(monitor=monitor).order_by('-id')[0]
            latest_check_status = latest_check.status

        if latest_check_status != status:
           models.MonitorHistory.objects.create(monitor=monitor,status=status,response=response,response_raw=response_raw)
        else:
            print ("Status has not changed")   
            pass



