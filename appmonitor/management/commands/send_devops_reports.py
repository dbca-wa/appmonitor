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

                        
                        work_items_data = []
                        for i in range(0, len(work_item_ids), batch_size):
                            batch_ids = work_item_ids[i:i + batch_size]
                            work_items = wit_client.get_work_items(ids=batch_ids)                        
                            for item in work_items:
                                row = []
                                for cas in column_array_system: 
                                    if cas == "System.Id":
                                        row.append(item.id)
                                    elif cas == "System.AssignedTo":
                                        assigned_obj = item.fields.get('System.AssignedTo')
                                        assigned_to = assigned_obj.get('displayName', 'Unassigned') if isinstance(assigned_obj, dict) else str(assigned_obj)        
                                        row.append(assigned_to)     
                                    elif cas == "System.CreatedDate":
                                        date_str = item.fields.get(cas)
                                        utc_datetime = parse_datetime(date_str)
                                        target_tz = timezone(timedelta(hours=8))
                                        django_datetime = utc_datetime.astimezone(target_tz)
                                        row.append(django_datetime)                                    
                                    else:
                                        row.append(item.fields.get(cas))
                                work_items_data.append(row)
                                # print (row)
                        # print (work_items_data)

                    t = email_templates.DevopsReportList()

                    t.subject = "Devops Report: "+str(df.name) + " (Total: "+str(total_tasks)+")"
                    to_addresses=[]
                    for notification in models.DevopsReportNotification.objects.filter(active=True,devopsreport=df):
                        print ("Preparing to "+notification.email)
                        to_addresses.append(notification.email)
            
                    t.send(to_addresses=to_addresses, context={"total_tasks": total_tasks, "priortystatus_index" : priortystatus_index , "sort_order": df.sort_order, "report_name": df.name, "column_array_table": column_array_table, "column_array_system": column_array_system, "work_items_data": work_items_data, "settings": settings})        
                                
                except Exception as e:
                    print ("Building Report Error")                
                    print (e)
                                

                    # for i in range(0, len(work_item_ids), batch_size):
                    #     batch_ids = work_item_ids[i:i + batch_size]
                    #     work_items = wit_client.get_work_items(ids=batch_ids)                        
                    #     for item in work_items:
                    #             project = item.fields.get('System.TeamProject')
                    #             item_id = item.id
                    #             state = item.fields.get('System.State')
                    #             title = item.fields.get('System.Title')
                    #             created_date = item.fields.get('System.CreatedDate')
                    #             workitem_type = item.fields.get('System.WorkItemType')            
                                            
                    #             # Extract assigned user's display name if it exists
                    #             assigned_obj = item.fields.get('System.AssignedTo')
                    #             assigned_to = assigned_obj.get('displayName', 'Unassigned') if isinstance(assigned_obj, dict) else str(assigned_obj)
                                
                    #             # Truncate long strings for cleaner terminal output formatting
                    #             print(f"{project[:100]:<100} {item_id:<8} {workitem_type:<8} {state:<20} {assigned_to[:28]:<30} {created_date:<30} {title} ")                        

            # for tf in devops_filters:         
            #     tickets_total = 0 
            #     tickets = []  
            #     tickets_array = []
            #     status_in_use = []

            #     try:

            #         tickets = requests.get(tf.url,auth=auth_request)
            #         tickets_pending = tickets.json()
            #         total_pages = 1
            #         if "total" in tickets_pending:
            #             total_tickets = tickets_pending['total']
            #             total_tickets_divide_into_pages = int(total_tickets) / 100
                        
                        
            #             if float(total_tickets_divide_into_pages) >= int(total_tickets_divide_into_pages):
            #                 total_pages = int(total_tickets_divide_into_pages) + 1
            #         page = 1
            #         while page <= total_pages:
            #             new_url = tf.url.replace("&page=1", "&page="+str(page))
            #             print (new_url)
            #             tickets = requests.get(new_url,auth=auth_request)
            #             tickets_pending = tickets.json()
                        
            #             if "tickets" in tickets_pending:
            #                 # tickets_total = len(tickets_pending['tickets'])
            #                 for t in tickets_pending['tickets']:
            #                     ticket_row = {}
            #                     ticket_row['id']  = t['id']
            #                     ticket_row['subject'] = t['subject']
            #                     # ticket_row['system_id'] = t['custom_fields']['system_id']
            #                     ticket_row['lf_system_id'] = t['custom_fields']['lf_system_id']
            #                     ticket_row['status'] = t['status']
            #                     if t['status'] not in status_in_use:
            #                         status_in_use.append(t['status'])

            #                     print (t['subject'])   
            #                     nowtime = datetime.now()
            #                     # print (t)             
                                
            #                     # created_at = t['created_at'].replace("T"," ")
            #                     # created_at = created_at.replace("Z","")
            #                     ticket_created_datetime = datetime.strptime(t['created_at'], '%Y-%m-%dT%H:%M:%SZ')  
            #                     ticket_row['ticket_created_datetime']  = ticket_created_datetime
            #                     timediff = nowtime - ticket_created_datetime
            #                     ticket_row['age'] = timediff.days

            #                     ticket_updated_datetime = datetime.strptime(t['updated_at'], '%Y-%m-%dT%H:%M:%SZ')                                       
            #                     ticket_row['ticket_updated_datetime'] = ticket_updated_datetime
            #                     timediff = nowtime - ticket_updated_datetime
            #                     ticket_row['age_updated'] = timediff.days

            #                     ticket_row['updated_at'] = t['updated_at']
            #                     ticket_row['created_at'] = t['created_at']
                        
            #                     tickets_array.append(ticket_row)
            #                     tickets_total = tickets_total + 1
            #             print ("Page "+str(page)+" of "+str(total_pages))
            #             page = page + 1

            #     except Exception as e:
            #         print (e)

            #     t = email_templates.TicketList()
            #     if tf.email_group == models.TicketFilter.EMAIL_GROUP.group_list:
            #         t = email_templates.TicketListGrouped()                                     
                
            #     t.subject = "Tickets Outstanding for "+str(tf.name) + " (Total: "+str(tickets_total)+")"
            #     to_addresses=[]
            #     for notification in models.TicketFilterNotification.objects.filter(active=True,ticket_filter=tf):
            #         print ("Preparing to "+notification.email)
            #         to_addresses.append(notification.email)
            #     t.send(to_addresses=to_addresses, context={"tickets": tickets_pending, "tickets_total": tickets_total, "settings": settings, "tickets_array": tickets_array, "ticket_systems" : ticket_systems, "ticket_status": ticket_status, "status_in_use": status_in_use, "test": {19: "test1", 17: "test2", 18: "test3"}})        
        

