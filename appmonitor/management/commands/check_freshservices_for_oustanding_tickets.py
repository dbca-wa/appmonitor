from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
import datetime
from appmonitor import models
from appmonitor import utils
from appmonitor import email_templates
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Send Notification for Outstanding Tickets'

    def handle(self, *args, **options):
            print ("Running Ticket Check")
           
            ticket_filters = models.TicketFilter.objects.filter(active=True)
            FRESHSERVICES_API_KEY = settings.FRESHSERVICES_API_KEY
            auth_request = requests.auth.HTTPBasicAuth(FRESHSERVICES_API_KEY, "X")
            
            for tf in ticket_filters:         
                tickets_total = 0 
                tickets = []       
                try:
                    tickets = requests.get(tf.url,auth=auth_request)
                    tickets_pending = tickets.json()
                    
                    if "tickets" in tickets_pending:
                         tickets_total = len(tickets_pending['tickets'])
                         for t in tickets_pending['tickets']:
                              print (t['subject'])                         
                except Exception as e:
                    print (e)

                t = email_templates.TicketList()
                t.subject = "Tickets Outstanding for "+str(tf.name) + " (Total: "+str(tickets_total)+")"
                to_addresses=[]
                for notification in models.TicketFilterNotification.objects.filter(active=True,ticket_filter=tf):
                    print ("Preparing to "+notification.email)
                    to_addresses.append(notification.email)
                t.send(to_addresses=to_addresses, context={"tickets": tickets_pending, "tickets_total": tickets_total, "settings": settings})        
        

