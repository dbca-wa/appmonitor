from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
import datetime
from appmonitor import models

class Command(BaseCommand):
    help = 'Remove old logs.'

    def handle(self, *args, **options):
        days_for_deletion = datetime.datetime.now() - datetime.timedelta(days=20)
        models.APIServiceLog.objects.filter(created__lt=days_for_deletion).delete()

