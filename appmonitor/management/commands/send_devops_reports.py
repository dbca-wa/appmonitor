from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
import datetime
from appmonitor import models
from appmonitor import utils
from appmonitor import email_templates
from django.conf import settings
from datetime import datetime
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from django.utils.dateparse import parse_datetime
from datetime import timezone, timedelta
import requests
import os

class Command(BaseCommand):
    help = 'Send Devops Reports'

    def add_arguments(self, parser):
        parser.add_argument('-i' '--id', type=str , help='Only run selected report by id', default=None)

    def handle(self, *args, **options):
            print ("Running Devops Reports")
            devops_report_id = options['i__id']          
            if devops_report_id is None:
                devops_filters = models.DevopsReport.objects.filter(active=True)
            else:
                devops_filters = models.DevopsReport.objects.filter(active=True, id=devops_report_id)
            AZURE_DEVOPS_PAT = settings.AZURE_DEVOPS_PAT

            for df in devops_filters:
                print (df)
                try:
                    credentials = BasicAuthentication('', AZURE_DEVOPS_PAT)
                    connection = Connection(base_url=df.devopsurl, creds=credentials)
                    wit_client = connection.clients.get_work_item_tracking_client() 
                    wiql_query = wiql_query = { 'query': df.wiql_query  }
                    
                    print("Fetching all tasks across all projects for {} with id {}... (This may take a moment)".format(df.name, df.id))
                    query_result = wit_client.query_by_wiql(wiql_query)   
                    work_item_ids = [item.id for item in query_result.work_items]     
                    if not work_item_ids:
                        print("No tasks found in the organization.")               
                    else:
                        print(f"Found {len(work_item_ids)} total tasks. Fetching details...\n")                    
                        total_tasks = len(work_item_ids)
                        batch_size = 200          
                        column_array_table = [col.reference_name.replace("System.","").replace("Custom.","") for col in query_result.columns]
                        column_array_system = [col.reference_name for col in query_result.columns]

                        # print(f"Columns in array: {column_array_system}")
                        column_index = 1
                        priortystatus_index = None
                        for cas in column_array_system:
                            if cas == 'Custom.PriorityStatus':
                                priortystatus_index = column_index
                            column_index = column_index + 1

                        column_index = 1
                        task_id_index = None
                        for cas in column_array_system:
                            if cas == 'System.Id':
                                task_id_index = column_index
                                # column_array_table.append("TaskLink")
                                # column_array_system.append("System.Task")
                            column_index = column_index + 1                            

                        
                        work_items_data = []
                        for i in range(0, len(work_item_ids), batch_size):
                            batch_ids = work_item_ids[i:i + batch_size]
                            work_items = wit_client.get_work_items(ids=batch_ids)                        
                            for item in work_items:
                                row = {}
                                # row = []
                                for cas in column_array_system: 
                                    if cas == "System.Id":
                                        row["System.Id"] = {"id" : item.id, "url" : "{}/{}/_workitems/edit/{}/".format(df.devopsurl, item.fields.get('System.TeamProject'),  str(item.id)) }
                                        #row.append(item.id)
                                    elif cas == "System.AssignedTo":
                                        assigned_obj = item.fields.get('System.AssignedTo')
                                        assigned_to = assigned_obj.get('displayName', 'Unassigned') if isinstance(assigned_obj, dict) else str(assigned_obj)        
                                        # row.append(assigned_to)   
                                        row["System.AssignedTo"] = assigned_to
                                    elif cas == "System.CreatedDate":
                                        date_str = item.fields.get(cas)
                                        utc_datetime = parse_datetime(date_str)
                                        target_tz = timezone(timedelta(hours=8))
                                        django_datetime = utc_datetime.astimezone(target_tz)
                                        # row.append(django_datetime)     
                                        row["System.CreatedDate"] = django_datetime                               
                                    else:
                                        # row.append(item.fields.get(cas))
                                        row[cas] = item.fields.get(cas) 

                                work_items_data.append(row)
                                # print (row)
                        # print (work_items_data)

                    t = email_templates.DevopsReportList()

                    t.subject = "Devops Report: "+str(df.name) + " (Total: "+str(total_tasks)+")"
                    to_addresses=[]
                    for notification in models.DevopsReportNotification.objects.filter(active=True,devopsreport=df):
                        print ("Preparing to "+notification.email)
                        to_addresses.append(notification.email)
            
                    t.send(to_addresses=to_addresses, context={"total_tasks": total_tasks, "priortystatus_index" : priortystatus_index , "task_id_index" : task_id_index, "sort_order": df.sort_order, "report_name": df.name, "column_array_table": column_array_table, "column_array_system": column_array_system, "work_items_data": work_items_data, "settings": settings})        
                                
                except Exception as e:
                    print ("Building Report Error")                
                    print (e)
                                

            