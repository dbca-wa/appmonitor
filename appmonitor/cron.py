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
    RUN_WEEKLY_ON_DAYS = [1, 2, 3, 4, 5]
    RUN_AT_TIMES = ['20:00']
    schedule = django_cron.Schedule(run_at_times=RUN_AT_TIMES)
    code = "appmonitor.email_checks"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("IT Checks Notification cron job triggered, running...")

        # Run Management Command
        management.call_command("notification_email_checks")
        return "Job Completed Successfully"
    

class CronJobNotificationEmailWeekends(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    RUN_WEEKLY_ON_DAYS = [0, 6]
    RUN_AT_TIMES = ['9:00']
    schedule = django_cron.Schedule(run_at_times=RUN_AT_TIMES)
    code = "appmonitor.email_checks"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("IT Checks Notification cron job triggered, running...")

        # Run Management Command
        management.call_command("notification_email_checks")
        return "Job Completed Successfully"