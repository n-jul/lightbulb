from django.contrib import admin

# Register your models here.
from django_celery_beat.models import PeriodicTask, IntervalSchedule

admin.site.register(PeriodicTask)
admin.site.register(IntervalSchedule)