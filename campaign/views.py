from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.models import User as DjangoUser
from .serializers import EmailSerializer
from .models import UserCampaign
from .serializers import UserCampaignSerializer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from extended_user.models import extended_user
import logging

# Create a logger for this file
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def check_if_superadmin(user_id):
    """
    Checks if a given user ID exists in the database and if their role is 'superadmin'.
    Returns True if user exists and is a superadmin, otherwise False.
    """
    logger.info(f"Checking superadmin status for user_id: {user_id}")
    try:
        user = session.query(extended_user).filter_by(id=user_id).first()
        
        if user and user.role == 'superadmin':
            logger.info(f"User {user_id} confirmed as superadmin")
            return True
        logger.warning(f"User {user_id} is not a superadmin or doesn't exist")
        return False
        
    except Exception as e:
        logger.error(f"Error checking superadmin status for user {user_id}: {str(e)}", exc_info=True)
        return False
    finally:
        session.close()

class SendTestEmailViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for sending test emails.
    """
    def create(self, request):
        logger.info("Received request to send test email")
        serializer = EmailSerializer(data=request.data)

        if serializer.is_valid():
            sender_id = serializer.validated_data["sender_id"]
            logger.debug(f"Checking if sender with ID {sender_id} is an admin")
            sender = session.query(extended_user).filter(extended_user.id == sender_id).first()

            if not sender or sender.role != 'admin':
                logger.warning(f"Sender with ID {sender_id} is not authorized to send emails")
                return Response({"error": "You are not authorized to send emails"}, 
                                status=status.HTTP_403_FORBIDDEN)

            campaign = session.query(UserCampaign).filter(UserCampaign.id==serializer.validated_data['campaign_id'], UserCampaign.status=="pending").first()    
            subject, message ="",""
            logger.info(f"campaign object that we got: {campaign}")
            if campaign:
                subject = campaign.text
                message = campaign.description
            try:
                logger.debug("Querying users with 'user' role")
                users_with_role = session.query(extended_user).filter(extended_user.role=='user')
                user_ids = [user.id for user in users_with_role]
                users_list = DjangoUser.objects.filter(id__in=user_ids).values_list('email', flat=True)
                total_users = len(users_list)
                
                logger.info(f"Attempting to send email to {total_users} users")
                logger.info(f"Recipient list is {users_list}")
                send_mail(subject=subject, message=message,from_email="anjulkushwaha11@gmail.com", recipient_list=users_list)
                logger.info("Email sent successfully")
                
                return Response({"message": "Email sent successfully!", "Total users":total_users}, 
                              status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}", exc_info=True)
                return Response({"error": "Failed to send email"}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.warning(f"Invalid email data provided: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCampaignViewSet(viewsets.ViewSet):
    """
    A viewset for viewing and creating user campaigns using SQLAlchemy.
    """
    def create(self, request, *args, **kwargs):
        logger.info("Received request to create new user campaign")
        logger.debug(f"Request data: {request.data}")
        user_id = request.data.get('created_by', None)
        
        if not user_id:
            logger.warning("No user ID provided in campaign creation request")
            return Response({'error': "No user ID provided."}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        if not check_if_superadmin(user_id):
            logger.warning(f"Non-superadmin user {user_id} attempted to create campaign")
            return Response({'error': "You don't have the permission to create the campaign..."})

        serializer = UserCampaignSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid campaign data provided: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
                logger.debug(f"serializer: {serializer}")
                user_campaign_data = serializer.validated_data
                logger.debug(f"Data from serializer: {serializer.validated_data}")
                logger.debug(f"Creating new campaign with data: {user_campaign_data}")
                
                new_campaign = UserCampaign(
                    type=user_campaign_data['type'],
                    text=user_campaign_data['text'],
                    description=user_campaign_data.get('description', ''),
                    created_by=user_campaign_data['created_by'],
                    status=user_campaign_data['status'],
                )
                session.add(new_campaign)
                session.commit()
                logger.info(f"Successfully created new campaign by user {user_id}")
                
                response_serializer = UserCampaignSerializer(new_campaign)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create campaign: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()
    def list(self, request, *args, **kwargs):
        logger.info("Received request to list all user campaigns")
        try:
            campaigns = session.query(UserCampaign).all()
            campaign_count = len(campaigns)
            logger.info(f"Successfully retrieved {campaign_count} campaigns")
            
            serializer = UserCampaignSerializer(campaigns, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to retrieve campaigns: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()