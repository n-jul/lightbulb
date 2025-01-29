import os
import sys
import django
import json

# ✅ Step 1: Add the project root to Python's path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # This gets the directory where cron_script.py is located
sys.path.append(PROJECT_ROOT)  # Add project root to system path
sys.path.append(os.path.join(PROJECT_ROOT, "lightbulb"))  # Ensure Django project folder is included

# ✅ Step 2: Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lightbulb.settings")  # Make sure this matches your project name
django.setup()

# ✅ Step 3: Now import Django models AFTER setting up Django
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# ✅ Step 4: Create an Interval Schedule (if not already created)
schedule, created = IntervalSchedule.objects.get_or_create(
    every=1,  # Run every 1 minute
    period=IntervalSchedule.MINUTES
)

# ✅ Step 5: Create a Periodic Task (only if it doesn't already exist)
if not PeriodicTask.objects.filter(name="Send Email Every 1 Minute").exists():
    PeriodicTask.objects.create(
        interval=schedule,
        name="Send Email Every 1 Minute",  # Unique name
        task="campaign.tasks.add",  # Ensure this task exists in tasks.py
        args=json.dumps(["recipient@example.com"]),  # Arguments in JSON format
    )
    print("✅ Scheduled Task Created Successfully!")
else:
    print("⚠️ Task Already Exists. No changes made.")
