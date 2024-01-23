from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
import datetime
from appmonitor import models
from appmonitor import utils
from appmonitor import email_templates
from django.conf import settings

class Command(BaseCommand):
    help = 'Send IT Checks Notification'

    def handle(self, *args, **options):
            print ("Running Notificaiton Job")
            checks = utils.get_checks(None,None)
            manual_checks = models.ManualCheck.objects.filter(active=True)
            t = email_templates.AppCheckList()
            to_addresses=[]
            for notification in models.NotificationEmail.objects.all():
                print ("Preparing to "+notification.email)
                to_addresses.append(notification.email)
            t.send(to_addresses=to_addresses, context={"checks": checks, "manual_checks": manual_checks, "settings": settings}, headers={"Reply-To": settings.IT_CHECKS_REPLY_TO_EMAIL})        
        

