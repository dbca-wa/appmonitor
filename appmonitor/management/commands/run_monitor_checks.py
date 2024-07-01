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
import shareplum
import urllib
import subprocess, platform
import requests
import socket
import threading
import datetime
import json
import re
import psycopg2
import time

from appmonitor import models
from appmonitor import email_templates

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

            if i.mon_type == 2:
                thread = threading.Thread(target=self.ping, args=(i,i.host,))
                thread.start()

            if i.mon_type == 3:
                thread = threading.Thread(target=self.socket, args=(i,i.host,int(i.port),))
                thread.start()

            if i.mon_type == 5:
                  thread = threading.Thread(target=self.get_ssl_expiry, args=(i,i.host,int(i.port),))
                  thread.start()

            if i.mon_type == 6:
                 thread = threading.Thread(target=self.ping2, args=(i,i.host,10,1))
                 thread.start()

            if i.mon_type == 7:
                 thread = threading.Thread(target=self.ping2, args=(i,i.host,10,1))
                 thread.start()

            if i.mon_type == 8:
                  thread = threading.Thread(target=self.get_json_key_check, args=(i,))
                  thread.start()

            if i.mon_type == 9:
                  thread = threading.Thread(target=self.get_http_status_code, args=(i,i.url, i.status_code))
                  thread.start()
            if i.mon_type == 10:
                  thread = threading.Thread(target=self.get_sharepoint_auth, args=(i,))
                  thread.start()  

            if i.mon_type == 11:
                  thread = threading.Thread(target=self.db_timing_check, args=(i,))
                  thread.start()  

            if i.mon_type == 12:
                  thread = threading.Thread(target=self.db_query_check, args=(i,))
                  thread.start()  
        #thread still keep running not accurate finished time.  work in progress                  
        #mjl.finished = datetime.datetime.today()
        #mjl.save()

    def db_query_check(self, monitor):
        html_str = ''
        try:
            conn = psycopg2.connect(database=monitor.db_name, 
                    user=monitor.db_username, 
                    password=monitor.db_password,
                    host=monitor.db_host,                   
                    port = monitor.db_port)
            cursor = conn.cursor()
            
            cursor.execute(monitor.db_query)
            rows = cursor.fetchall()
            row_one_column_one = rows[0][0]
        except Exception as e:           
            print (e)
            html_str = str(e)

        try:
            if monitor.check_operator == 1:
                if int(row_one_column_one) > int(monitor.up_value):
                    self.create_monitor_history(monitor,3,'Success ', row_one_column_one)
                elif int(row_one_column_one) > int(monitor.warn_value):
                    self.create_monitor_history(monitor,2,'Warn', row_one_column_one)
                else:
                    self.create_monitor_history(monitor,1,'Down', row_one_column_one)  

            if monitor.check_operator == 2:
                if int(row_one_column_one) < int(monitor.up_value):
                    self.create_monitor_history(monitor,3,'Success ', row_one_column_one)
                elif int(row_one_column_one) < int(monitor.warn_value):
                    self.create_monitor_history(monitor,2,'Warn', row_one_column_one)
                else:
                    self.create_monitor_history(monitor,1,'Down', row_one_column_one)  

            if monitor.check_operator == 3:
                if int(row_one_column_one) == int(monitor.up_value):
                    self.create_monitor_history(monitor,3,'Success ', row_one_column_one)
                else:
                    self.create_monitor_history(monitor,1,'Down', row_one_column_one)  

            if monitor.check_operator == 4:
                if str(row_one_column_one) == str(monitor.up_value):
                    self.create_monitor_history(monitor,3,'Success ', row_one_column_one)
                else:
                    self.create_monitor_history(monitor,1,'Down', row_one_column_one+":"+html_str)    
  
        except Exception as e:
            print (e)
            self.create_monitor_history(monitor,1,'Error', str(e)+":"+html_str)

        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()

    def db_timing_check(self, monitor):

        html_str = ''
        try:

            conn = psycopg2.connect(database=monitor.db_name, 
                    user=monitor.db_username, 
                    password=monitor.db_password,
                    host=monitor.db_host,                   
                    port = monitor.db_port)
            cursor = conn.cursor()
            tic = time.time()
            cursor.execute(monitor.db_query)
            toc = time.time()
            time_lapse = toc - tic
        except Exception as e:           
            print (e)
            html_str = str(e)
            auth_passed = False

        try:
            if int(time_lapse) < int(monitor.up_value):
                self.create_monitor_history(monitor,3,'Success ', time_lapse)
            elif int(time_lapse) < int(monitor.warn_value):
                self.create_monitor_history(monitor,2,'Warn', time_lapse)
            else:
                self.create_monitor_history(monitor,1,'Down', time_lapse)   
  
        except Exception as e:
            print (e)
            self.create_monitor_history(monitor,1,'Error', str(e)+":"+html_str)

        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()

    def get_sharepoint_auth(self, monitor):

        auth_passed = False
        html_str = ''
        try:
            auth_url = urllib.parse.urljoin(monitor.sharepoint_url, "/")
            auth = shareplum.Office365(auth_url, monitor.sharepoint_username, monitor.sharepoint_password)
            site = shareplum.Site(monitor.sharepoint_url, authcookie=auth.get_cookies(), version=shareplum.site.Version.v365)
            auth_passed = True
        except Exception as e:           
            print (e)
            html_str = str(e)
            auth_passed = False

        if auth_passed is True:
            self.create_monitor_history(monitor,3,'auth passed', html_str)
        else:
            self.create_monitor_history(monitor,1,'auth failed',html_str)

        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()


    def get_website(self, monitor,website,string_check):      
        print (monitor.check_name)
        response = None
        html_str = ''
        cookies={}
        auth_response=None
        response_code = ""
        if monitor.use_basic_auth is True:
            
            try:
                auth_response=auth=HTTPBasicAuth(monitor.username,monitor.password)                
            except Exception as e:
                html_str="Error loading basic auth"
                print (e)                
                
        try:
            response = requests.get(website, timeout=30, cookies=cookies, auth=auth_response)   
            response_code = response.status_code 
            print (response.status_code)     
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
              self.create_monitor_history(monitor,3,'string found', "Response Code: "+str(response_code)+"\n"+html_str)
           else:
              self.create_monitor_history(monitor,1,'string not found',"Response Code: "+str(response_code)+"\n"+html_str)
        else:
           if '-!STATUSCHECK!-' in html_str:
              self.create_monitor_history(monitor,3,'string found',"Response Code: "+str(response_code)+"\n"+html_str)
           else:
              self.create_monitor_history(monitor,1,'string not found',"Response Code: "+str(response_code)+"\n"+html_str)

        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()

    def get_http_status_code(self, monitor,website,status_code):      
        print (monitor.check_name)
        response = None
        html_str = ''
        cookies={}
        auth_response=None
        response_code = -1000
        if monitor.use_basic_auth is True:
            
            try:
                auth_response=auth=HTTPBasicAuth(monitor.username,monitor.password)                
            except Exception as e:
                html_str="Error loading basic auth"
                print (e)                
                
        try:
            response = requests.get(website, timeout=30, cookies=cookies, auth=auth_response)   
            response_code = response.status_code 
            print (response.status_code)     
        except Exception as e:
            print (e)
            html_str = str(e)
            response = None
            pass
        
        
        if status_code == response_code:
            self.create_monitor_history(monitor,3,'HTTP Status Code Match', "Response Code: "+str(response_code)+"\n"+html_str)
        else:
            self.create_monitor_history(monitor,1,'Incorrect HTTP Status Code',"Response Code: "+str(response_code)+"\n"+html_str)
        
        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()

    def ping(self,monitor,host):
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

        # Ping command count option as function of OS
        param = '-n' if system_name().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '4', host]
        ping_response = system_call(command, stdout=DEVNULL, stderr=STDOUT) == 0

        if ping_response is True:
           self.create_monitor_history(monitor,3,'ping success',ping_response)
        else:
           self.create_monitor_history(monitor,1,'ping failed',ping_response)

        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()

    def ping2(self, monitor, server='www.google.com', count=1, wait_sec=1):
        """
        :rtype: dict or None
        """
        print ("RUNNING PING 2")
        resp = {}
        output = ""
        cmd = "ping -c {} -W {} {}".format(count, wait_sec, server).split(' ')
        try:
            output = subprocess.check_output(cmd).decode().strip()
            lines = output.split("\n")
            total = lines[-2].split(',')[3].split()[1]
            loss = lines[-2].split(',')[2].split()[0]
            timing = lines[-1].split()[3].split('/')
            resp = {
                'type': 'rtt',
                'min': timing[0],
                'avg': timing[1],
                'max': timing[2],
                'mdev': timing[3],
                'total': total,
                'loss': loss,
            }
            
        except Exception as e:
            print(e)
            output = str(e)
            resp = {'avg': None,'loss' : '100%'}
        print ("PING 2 OUT PUT")
        print (output)
        print (resp)
        if monitor.mon_type == 6:
            if resp['avg'] is None:
                 self.create_monitor_history(monitor,0,'unknown latency', output)
            else:
                if float(resp['avg']) >= int(monitor.down_value):
                   self.create_monitor_history(monitor,1,'latency : '+str(resp['avg']), output)
                elif float(resp['avg']) >= int(monitor.warn_value):
                   self.create_monitor_history(monitor,2,'latency : '+str(resp['avg']), output)
                elif float(resp['avg']) >= int(monitor.up_value):
                   self.create_monitor_history(monitor,3,'latency : '+str(resp['avg']), output)
                else:
                   self.create_monitor_history(monitor,0,'no latency matches for down/warn/up.  Check values', output)

        if monitor.mon_type == 7:
            if int(resp['loss'].rstrip("%")) >= int(monitor.down_value):
                self.create_monitor_history(monitor,1,'packet loss : '+str(resp['loss']), output)
            elif int(resp['loss'].rstrip("%")) >= int(monitor.warn_value):
                self.create_monitor_history(monitor,2,'packet loss : '+str(resp['loss']), output)
            elif int(resp['loss'].rstrip("%")) >= int(monitor.up_value):
                self.create_monitor_history(monitor,3,'packet loss : '+str(resp['loss']), output)
        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()


    def socket(self,monitor,host,port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(50)
        result = None

        try:
           result = sock.connect_ex((host,port))
        except socket.gaierror:
           pass

        if result == 0:
           self.create_monitor_history(monitor,3,'socket success',result)
        else:
           self.create_monitor_history(monitor,1,'socket failed',result)

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

    def get_json_key_check(self, monitor):


        response = None
        html_str = ''
        cookies={}
        auth_response=None
        response_code = ""
        global jsonvalue 
        jsonvalue = ""
        jsonresponse = {}

        if monitor.use_basic_auth is True:    
            try:
                auth_response=auth=HTTPBasicAuth(monitor.username,monitor.password)                
            except Exception as e:
                html_str="Error loading basic auth"
                print (e)                
                
        try:

            response = requests.get(monitor.url, timeout=30, cookies=cookies, auth=auth_response)   
            response_code = response.status_code
            jsonresponse = json.loads(response.text)            
            exec_obj  = {'jsonvalue':jsonvalue,'jsonresponse':jsonresponse}
            exec("jsonvalue = "+monitor.json_key, exec_obj)            
            jsonvalue = exec_obj['jsonvalue']
            
        except Exception as e:
            print (e)
            html_str = str(e)
            response = None
            pass
        

        try:
            if monitor.check_operator == 1:
                if int(jsonvalue) > int(monitor.up_value):
                    self.create_monitor_history(monitor,3,'Success ', jsonresponse)
                elif int(jsonvalue) > int(monitor.warn_value):
                    self.create_monitor_history(monitor,2,'Warn', jsonresponse)
                else:
                    self.create_monitor_history(monitor,1,'Down', jsonresponse)  

            if monitor.check_operator == 2:
                if int(jsonvalue) < int(monitor.up_value):
                    self.create_monitor_history(monitor,3,'Success ', jsonresponse)
                elif int(jsonvalue) < int(monitor.warn_value):
                    self.create_monitor_history(monitor,2,'Warn', jsonresponse)
                else:
                    self.create_monitor_history(monitor,1,'Down', jsonresponse)  

            if monitor.check_operator == 3:
                if int(jsonvalue) == int(monitor.up_value):
                    self.create_monitor_history(monitor,3,'Success ', jsonresponse)
                else:
                    self.create_monitor_history(monitor,1,'Down', jsonresponse)  

            if monitor.check_operator == 4:
                if str(jsonvalue) == str(monitor.up_value):
                    self.create_monitor_history(monitor,3,'Success ', jsonresponse)
                else:
                    self.create_monitor_history(monitor,1,'Down', jsonresponse)  
        except Exception as e:
            print (e)
            self.create_monitor_history(monitor,1,'Error', str(e)) 

        a = dt_datetime.now()
        monitor.last_update =a
        monitor.save()


    def create_monitor_history(self,monitor,status,response, response_raw):
        latest_check_status = -1
        latest_check = None
        if models.MonitorHistory.objects.filter(monitor=monitor).exists():
            latest_check = models.MonitorHistory.objects.filter(monitor=monitor).order_by('-id')[0]
            latest_check_status = latest_check.status

        print ("CHECK STATUS"+monitor.check_name)
        if latest_check_status != status:
            # Log status change
            models.MonitorHistory.objects.create(monitor=monitor,status=status,response=response,response_raw=response_raw)
  
            # Send notification
            monitor_alerts = models.MonitorAlert.objects.filter(monitor=monitor)
            print ("SENDING MONITOR ALERT")
            status_icon = "⚫️"
            status_name = "UNKNOWN"

            if status == 1:
                status_icon = '🚨'
                status_name = 'DOWN'
            elif status == 2:
                status_icon  = '⚠️'
                status_name = 'WARN'
            elif status == 3:
                status_icon  = '✅'
                status_name = 'UP'                

      
            for ma in monitor_alerts:
                t = email_templates.MonitorSensorAlert()
                t.subject = status_icon+" Sensor Alert "+monitor.check_name
                to_addresses=[]  
                print (ma)                                                
                if ma.no_html_email is True:
                    t.html_template = None
                print ("Preparing email for "+ma.email)
                to_addresses.append(ma.email)
                t.send(to_addresses=to_addresses, context={"monitor": monitor, "status": status, "settings": settings, "status": status, 'status_icon': status_icon,'status_name' : status_name, 'latest_check' : latest_check})     


        else:
            print ("Status has not changed")   
            pass



