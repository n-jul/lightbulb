from celery import shared_task
from django.core.mail import send_mail
import logging
logger = logging.getLogger(__name__)

@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    if isinstance(recipient_list, str):  # Convert string to a proper list
        import ast
        recipient_list = ast.literal_eval(recipient_list)
    logger.critical(f"Logger+++++++++++++++++++++++++++++++++++++")
    send_mail(subject, message, from_email, recipient_list)
    
@shared_task
def add():
    logger.info("✅ Hello from Celery Task!")
    
    