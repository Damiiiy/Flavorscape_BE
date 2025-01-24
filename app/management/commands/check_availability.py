import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from app.models import Table, Waitlist


class Command(BaseCommand):
    help = 'Checks for table availability and notifies users on the waitlist.'

    def handle(self, *args, **kwargs):
        # Get the current date
        today = datetime.date.today()

        # Get all tables that are currently available
        available_tables = Table.objects.filter(availability_status=True)

        # If there are available tables, proceed with checking the waitlist
        if available_tables.exists():
            for table in available_tables:
                # Find waitlist entries for this table and today's date
                waitlist_entries = Waitlist.objects.filter(table=table, date=today, status="waiting")

                # Notify each user on the waitlist
                for entry in waitlist_entries:
                    try:
                        # Send email notification to the user
                        send_mail(
                            subject='Table Available Notification',
                            message=f'Dear {entry.user.full_name},\n\n'
                                    f'A table (Table {table.table_number}) is now available on {today}.\n'
                                    f'Please log in to confirm your reservation.',
                            from_email='no-reply@flavorscape.com',
                            recipient_list=[entry.user.email],
                            fail_silently=False,
                        )

                        # After sending the email, update the waitlist status to 'notified'
                        entry.status = 'notified'
                        entry.save()

                        # Log success to the command output
                        self.stdout.write(self.style.SUCCESS(
                            f'Notified {entry.user.email} for table {table.table_number}.'
                        ))

                    except Exception as e:
                        # If an error occurs while sending the email, log it to stderr
                        self.stderr.write(f"Failed to notify {entry.user.email}: {str(e)}")
        else:
            # If no available tables are found, log that information
            self.stdout.write(self.style.SUCCESS('No available tables found to notify waitlist users.'))













# # app/management/check_availability.py
# import datetime
# from django.core.management.base import BaseCommand
# from django.core.mail import send_mail
# from app.models import Table, Waitlist


# class Command(BaseCommand):
#     help = 'Checks for table availability and notifies users on the waitlist.'

#     def handle(self, *args, **kwargs):
#         # Get the current date
#         today = datetime.date.today()

#         # Get all tables that are now available
#         available_tables = Table.objects.filter(availability_status=True)

#         if available_tables.exists():
#             for table in available_tables:
#                 # Find waitlist entries for this table and today
#                 waitlist_entries = Waitlist.objects.filter(table=table, date=today, status="waiting")

#                 for entry in waitlist_entries:
#                     # Send an email notification
#                     try:
#                         send_mail(
#                             subject='Table Available Notification',
#                             message=f'Dear {entry.user.full_name},\n\n'
#                                     f'A table (Table {table.table_number}) is now available on {today}.\n'
#                                     f'Please log in to confirm your reservation.',
#                             from_email='no-reply@flavorscape.com',
#                             recipient_list=[entry.user.email],
#                             fail_silently=False,
#                         )
#                         # Update waitlist status to 'notified'
#                         entry.status = 'notified'
#                         entry.save()

#                         self.stdout.write(self.style.SUCCESS(
#                             f'Notified {entry.user.email} for table {table.table_number}.'
#                         ))
#                     except Exception as e:
#                         self.stderr.write(f"Failed to notify {entry.user.email}: {str(e)}")



