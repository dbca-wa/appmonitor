"""APP Monitor Django Application Cron Jobs."""

# Standard
import logging

# Third-Party
from django import conf
from django.core import management
import django_cron

# Logging
log = logging.getLogger(__name__)



class CronJobNotificationEmail(django_cron.CronJobBase):
    """Cron Job for the Catalogue Scanner."""
    RUN_AT_TIMES = ['8:00','21:00']
    schedule = django_cron.Schedule(run_at_times=RUN_AT_TIMES))
    code = "appmonitor.email_checks"

    def do(self) -> None:
        """Perform the Scanner Cron Job."""
        # Log
        log.info("Scanner cron job triggered, running...")

        # Run Management Command
        management.call_command("notification_email_checks")