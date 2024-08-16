"""APP Monitor Django Application Cron Jobs."""

# Standard
import logging

# Third-Party
from django import conf
from django.core import management
import django_cron

# Logging
log = logging.getLogger(__name__)



class CronJobNotificationEmailWeekDays(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    RUN_ON_DAYS = [0, 1, 2, 3, 4, 5, 6]
    RUN_AT_TIMES = ['20:00']
    dc = django_cron.Schedule()
    dc_items = dc.__dict__
    schedule = None
    if 'run_weekly_on_days' in dc_items: 
        print (dc_items)
        schedule = django_cron.Schedule(run_weekly_on_days=RUN_ON_DAYS,run_at_times=RUN_AT_TIMES)    
    else:
        schedule = django_cron.Schedule(run_on_days=RUN_ON_DAYS,run_at_times=RUN_AT_TIMES)
        
        
    code = "appmonitor.weekdays"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("IT Checks Notification cron job triggered, running...")

        # Run Management Command
        management.call_command("notification_email_checks")
        return "Job Completed Successfully"
    

class CronJobNotificationEmailWeekends(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    RUN_ON_DAYS = [0, 1, 2, 3, 4, 5, 6]
    RUN_AT_TIMES = ['6:30']
    dc = django_cron.Schedule()
    dc_items = dc.__dict__
    schedule = None
    if 'run_weekly_on_days' in dc_items: 
        print (dc_items)
        schedule = django_cron.Schedule(run_weekly_on_days=RUN_ON_DAYS,run_at_times=RUN_AT_TIMES)    
    else:
        schedule = django_cron.Schedule(run_on_days=RUN_ON_DAYS,run_at_times=RUN_AT_TIMES)
    
    code = "appmonitor.weekends"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("IT Checks Notification cron job triggered, running...")

        # Run Management Command
        management.call_command("notification_email_checks")
        return "Job Completed Successfully"
    
class CronJobDBArchive(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    RUN_ON_DAYS = [0, 1, 2, 3, 4, 5, 6]
    RUN_AT_TIMES = ['8:00']    
    dc = django_cron.Schedule()
    dc_items = dc.__dict__
    schedule = None
    if 'run_weekly_on_days' in dc_items:         
        schedule = django_cron.Schedule(run_weekly_on_days=RUN_ON_DAYS,run_at_times=RUN_AT_TIMES)    
    else:
        schedule = django_cron.Schedule(run_on_days=RUN_ON_DAYS,run_at_times=RUN_AT_TIMES)
    code = "appmonitor.dbarchive"

    def do(self) -> None:
        """Make of backup of the sqlite database directory."""
        
        # Run Management Command
        management.call_command("db_archive")
        return "Job Completed Successfully"