# from celery import shared_task
# from django.core.mail import send_mail
# from .models import  *

# @shared_task
# def check_table_availability_and_notify():
#     """
#     Check table availability and notify users on the waitlist.
#     """
#     unavailable_tables = Table.objects.filter(availability_status=False)

#     for table in unavailable_tables:
#         # Fetch the first user on the waitlist
#         waitlist_entries = Waitlist.objects.filter(table=table, status="waiting").order_by('created_at')

#         if waitlist_entries.exists():
#             waitlist_entry = waitlist_entries.first()

#             # Notify the user via email
#             send_mail(
#                 subject="Table Availability Notification",
#                 message=f"Good news! Table {table.table_number} is now available on {waitlist_entry.date}. "
#                         "Please confirm your reservation as soon as possible.",
#                 from_email="no-reply@flavorscape.com",
#                 recipient_list=[waitlist_entry.user.email],
#                 fail_silently=True,
#             )

#             # Update the waitlist entry status
#             waitlist_entry.status = "notified"
#             waitlist_entry.save()
