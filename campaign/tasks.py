from celery import shared_task
from django.core.mail import send_mail
import logging
from datetime import date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from .models import UserCampaignSequence,UserCampaign
from extended_user.models import extended_user
from django.contrib.auth.models import User as DjangoUser
logger = logging.getLogger(__name__)
DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
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
    
@shared_task
def send_campaigns_periodically():
    """
    Fetches and sends pending campaigns scheduled for today.
    """
    today = date.today()
    
    try:
        # Fetch pending campaigns for today
        logger.debug("Fetching pending campaigns scheduled for today...")
        pending_campaigns = session.query(UserCampaignSequence).filter(
            # UserCampaignSequence.scheduled_date.date() == today,
            UserCampaignSequence.status == "pending"
        ).all()
        logger.info(f"Found {len(pending_campaigns)} pending campaigns.")

        # Fetch users with 'user' role
        logger.debug("Querying users with 'user' role...")
        users_with_role = session.query(extended_user).filter(extended_user.role == 'user').all()
        user_ids = [user.id for user in users_with_role]

        # Get user emails
        users_list = list(DjangoUser.objects.filter(id__in=user_ids).values_list('email', flat=True))
        total_users = len(users_list)
        logger.info(f"Found {total_users} users to send emails.")

        # Process each pending campaign
        for pending_campaign in pending_campaigns:
            try:
                # Fetch the associated campaign
                campaign = session.query(UserCampaign).filter(
                    UserCampaign.id == pending_campaign.user_campaign_id
                ).first()

                if not campaign:
                    logger.warning(f"Campaign not found for UserCampaignSequence ID {pending_campaign.id}")
                    continue

                logger.info(f"Sending campaign {campaign.id} - {campaign.text} to {total_users} users.")

                # Send email
                send_mail(
                    subject=campaign.text,
                    message=campaign.description,
                    from_email="anjul.kushwaha@practicenumbers.com",
                    recipient_list=users_list
                )

                # Update campaign status to 'sent'
                pending_campaign.status = "sent"
                session.commit()
                logger.info(f"Campaign {campaign.id} marked as 'sent'.")

            except Exception as e:
                logger.error(f"Error processing campaign {pending_campaign.id}: {str(e)}")
                session.rollback()  # Rollback transaction on error

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching campaigns: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")