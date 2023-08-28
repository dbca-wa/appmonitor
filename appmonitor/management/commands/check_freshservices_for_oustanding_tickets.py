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
    help = 'Send Notification for New Fresh Service Tickets'

    def handle(self, *args, **options):
            print ("Running Ticket Check")
            checks = utils.get_checks()
            ticket_filters = models.TicketFilter.objects.filter(active=True)
            FRESHSERVICES_API_KEY = settings.FRESHSERVICES_API_KEY
            auth_request = requests.auth.HTTPBasicAuth(FRESHSERVICES_API_KEY, "X")
            
            for tf in ticket_filters:         
                tickets = []       
                try:
                    tickets = requests.get(tf.url,auth=auth_request)
                    tickets_pending = tickets.json()
                    if "tickets" in tickets_pending:
                         for t in tickets_pending['tickets']:
                              print (t['subject'])                         
                except Exception as e:
                    print (e)

                t = email_templates.TicketList()
                to_addresses=[]
                for notification in models.TicketFilterNotification.objects.filter(active=True):
                    print ("Preparing to "+notification.email)
                    to_addresses.append(notification.email)
                t.send(to_addresses=to_addresses, context={"tickets": tickets_pending, "settings": settings})        
        
