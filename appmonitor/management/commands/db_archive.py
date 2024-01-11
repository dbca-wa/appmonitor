from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group
from django.conf import settings
import datetime
import shutil
import os
from appmonitor import models

class Command(BaseCommand):
    help = 'Backup sqlite database.'

    def handle(self, *args, **options):
        DAYS_TO_ARCHIVE = settings.DAYS_TO_ARCHIVE
        DB_ARCHIVE_DIR = str(settings.BASE_DIR)+'/'+settings.DB_ARCHIVE_DIR
        print (DB_ARCHIVE_DIR)
        if os.path.exists(DB_ARCHIVE_DIR):
            pass
        else:
            print ("Please create your DB_ARCHIVE_DIR {}".format(DB_ARCHIVE_DIR))
            return False

        print ("LASTEST DIRECTORY")
        LATEST_DIR = DB_ARCHIVE_DIR+'/'+str(DAYS_TO_ARCHIVE)
        if os.path.exists(LATEST_DIR):
            print (LATEST_DIR)
            shutil.rmtree(LATEST_DIR)

        count = 1
        # Create all archive directions 
        while count <= DAYS_TO_ARCHIVE:
            AR_DIR = DB_ARCHIVE_DIR+'/'+str(count)
        
            if os.path.exists(AR_DIR):
                print ("Aready Exists {}".format(AR_DIR))
            else:
                print ("Creating Exists {}".format(AR_DIR))
                os.makedirs(AR_DIR)
            count = count + 1

        count = DAYS_TO_ARCHIVE
        print ("Rotating Archives")
        while count >= 2:
            
            AR_DIR_SOURCE = DB_ARCHIVE_DIR+'/'+str(count -1)
            AR_DIR_TARGET = DB_ARCHIVE_DIR+'/'+str(count)
            # gather all files
            allfiles = os.listdir(AR_DIR_SOURCE)
            print (AR_DIR_SOURCE)
            print (AR_DIR_TARGET)
            # iterate on all files to move them to destination folder
            for f in allfiles:
                src_path = os.path.join(AR_DIR_SOURCE, f)
                dst_path = os.path.join(AR_DIR_TARGET, f)
                shutil.move(src_path, dst_path)

            count = count - 1
