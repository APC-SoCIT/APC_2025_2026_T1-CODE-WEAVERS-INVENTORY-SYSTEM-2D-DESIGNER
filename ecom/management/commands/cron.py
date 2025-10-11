from django.core.management.base import BaseCommand
from django_cron import CronJobBase, Schedule
from django.core.management import call_command

class UpdateOrderStatusCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # Run once per day (24 hours * 60 minutes)

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'ecom.update_order_status_cron_job'    # Unique code for this cron job

    def do(self):
        # Call the update_order_status management command
        call_command('update_order_status')