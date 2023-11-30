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
                            print ("TICKET")
                            print (t['subject']) 
                            print (t['updated_at'])

                            ticket_exists  = models.Tickets.objects.filter(ticket_reference_no=t['id'])

                            if ticket_exists.count() > 0:
                                print (ticket_exists[0])
                                updated_at = ticket_exists[0].last_update_str
                                if updated_at != t['updated_at']:
                                    ticket_new = email_templates.TicketUpdated()
                                    ticket_new.subject = "Updated Ticket : "+t['subject']+" "+str(t['id'])
                                    to_addresses=[]
                                    for notification in models.NewTicketFilterNotification.objects.filter(active=True,ticket_filter=tf):
                                        print ("Preparing to send updated "+notification.email)
                                        to_addresses.append(notification.email)
                                    ticket_new.send(to_addresses=to_addresses, context={"ticket": t, "settings": settings})   
                                    current_ticket = models.Tickets.objects.get(ticket_reference_no=t['id'])
                                    current_ticket.last_update_str = t['updated_at']
                                    current_ticket.save()

                            else:
                                ticket_new = email_templates.TicketNew()
                                ticket_new.subject = "New Ticket : "+t['subject']+" "+str(t['id'])
                                to_addresses=[]
                                for notification in models.NewTicketFilterNotification.objects.filter(active=True,ticket_filter=tf):
                                    print ("Preparing to send new "+notification.email)
                                    to_addresses.append(notification.email)
                                ticket_new.send(to_addresses=to_addresses, context={"ticket": t, "settings": settings})                                     

                                models.Tickets.objects.create(ticket_reference_no=t['id'],last_update_str = t['updated_at'])

                            
                except Exception as e:
                    print (e)


    
        

