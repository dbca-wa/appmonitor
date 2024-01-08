from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
import datetime
import requests
from appmonitor import models

class Command(BaseCommand):
    help = 'Remove old logs.'

    def handle(self, *args, **options):
        print ("Running Insecure DB Update.")
        INSECURE_LIST='https://raw.githubusercontent.com/pyupio/safety-db/master/data/insecure_full.json'
        if settings.INSECURE_LIST:
            INSECURE_LIST=settings.INSECURE_LIST

        insecure_list_json_string = requests.get(INSECURE_LIST)
        if insecure_list_json_string.status_code == 200:
            f = open(str(settings.BASE_DIR)+'/db/insecure_full.json', "wb")
            f.write(insecure_list_json_string.content)
            f.close()
            print ("Insecure DB Update Successful")
        else:
            print ("Insecure DB Update failed")
            print (insecure_list_json_string.status_code)
            print (insecure_list_json_string.content)





# create a management script to update the vulnerabilities database and save local

#