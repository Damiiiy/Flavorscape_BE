# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# # Set default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Flavorscape.settings')

# app = Celery('Flavorscape')

# # Use a string here to avoid serialization issues
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Autodiscover tasks from registered Django app configs.
# app.autodiscover_tasks()

# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
