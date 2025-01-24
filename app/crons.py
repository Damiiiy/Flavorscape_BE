import logging
from django_cron import CronJobBase, Schedule
from django.core.management import call_command

logger = logging.getLogger(__name__)

class CheckAvailabilityCronJob(CronJobBase):
    RUN_EVERY_MINS = 2  # Check every 2 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'app.check_availability'  # A unique identifier for this job

    def do(self):
        logger.info("Starting CheckAvailabilityCronJob")  # Debug log
        call_command('check_availability')
        logger.info("Completed CheckAvailabilityCronJob")  # Debug log
