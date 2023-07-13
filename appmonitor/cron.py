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
    schedule = django_cron.Schedule(run_on_days=RUN_ON_DAYS,run_at_times=RUN_AT_TIMES)
    code = "appmonitor.weekends"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("IT Checks Notification cron job triggered, running...")

        # Run Management Command
        management.call_command("notification_email_checks")
        return "Job Completed Successfully"