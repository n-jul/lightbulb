from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.core.mail import send_mail
from django.contrib.auth.models import User as DjangoUser
from .serializers import EmailSerializer, ScheduleCampaignSerializer
from .models import UserCampaign, UserMessage, UserCampaignSequence, AdminUserCampaign
from .serializers import UserCampaignSerializer,SuperAdminSendCampaignSerializer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_
from extended_user.models import extended_user
import logging
from .tasks import send_email_task
from django.utils.timezone import make_aware, is_aware, now, get_current_timezone, localtime
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError

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

def check_if_admin(user_id):
    """
    Checks if a given user ID exists in the database and if their role is 'admin'.
    Returns True if user exists and is a admin, otherwise False.
    """
    logger.info(f"Checking admin status for user_id: {user_id}")
    try:
        user = session.query(extended_user).filter_by(id=user_id).first()
        
        if user and user.role == 'admin':
            logger.info(f"User {user_id} confirmed as admin")
            return True
        logger.warning(f"User {user_id} is not a admin or doesn't exist")
        return False
        
    except Exception as e:
        logger.error(f"Error checking admin status for user {user_id}: {str(e)}", exc_info=True)
        return False
    finally:
        session.close()

def make_date_aware(dt):
    if dt and not is_aware(dt):
        return make_aware(dt)
    return dt
class IsSuperAdmin(BasePermission):
    """
    Custom permission to allow only superadmin users to access the view.
    """
    def has_permission(self, request, view):
        # Since user is already authenticated (checked by IsAuthenticated), 
        # just check if the user is a superadmin
        if check_if_superadmin(request.user.id):
            return True
        # If the user is not a superadmin
        return False

class IsAdmin(BasePermission):
    """
    Custom permission to allow only admin users to access the view.
    """
    def has_permission(self, request, view):
        # Since user is already authenticated (checked by IsAuthenticated), 
        # just check if the user is a admin
        if check_if_admin(request.user.id):
            return True

        # If the user is not a admin
        return False
class SendTestEmailViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for sending test emails.
    """
    # permission_classes=[IsAuthenticated, IsAdmin]
    def create(self, request):
        logger.info("Received request to send test email")
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['on_email']:
                send_now = serializer.validated_data["send_now"]
                scheduled_time = serializer.validated_data.get("scheduled_time")
                campaign = session.query(UserCampaign).filter(UserCampaign.id==serializer.validated_data['campaign_id'], UserCampaign.status=="pending").first()    
                subject, message ="",""
                logger.info(f"campaign object that we got: {campaign}")
                if campaign:
                    subject = campaign.text
                    message = campaign.description
                try:
                    logger.debug("Querying users with 'user' role")
                    admin_id = request.user.id
                    admin = session.query(extended_user).filter(extended_user.id == admin_id).first()
                    if admin and admin.practice_id:
                        practice_id_of_admin = admin.practice_id
                    users_with_role = session.query(extended_user).filter(
                        extended_user.role=='user',
                        extended_user.practice_id==practice_id_of_admin
                        )
                    user_ids = [user.id for user in users_with_role]
                    users_list = list(DjangoUser.objects.filter(id__in=user_ids).values_list('email', flat=True))
                    total_users = len(users_list)
                    
                    logger.info(f"Attempting to send email to {total_users} users")
                    logger.info(f"Recipient list is {users_list}")
                    if send_now or not scheduled_time:
                        send_email_task.apply_async(args=[subject, message, "anjulkushwaha11@gmail.com", users_list])
                        logger.info("Email sent successfully")
                        return Response({"message": "Email sent successfully!", "Total users":total_users}, status=status.HTTP_201_CREATED)
                    hardcoded_time = now()+timedelta(minutes=1)
                    send_email_task.apply_async(args=[subject, message, "anjulkushwaha11@gmail.com", users_list], eta=scheduled_time)
                    return Response({"message": "Email scheduled successfully!"})

                except Exception as e:
                    logger.error(f"Failed to send email: {str(e)}", exc_info=True)
                    return Response({"error": "Failed to send email"}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                campaign = session.query(UserCampaign).filter(UserCampaign.id==serializer.validated_data['campaign_id']).first()    
                logger.info(f"campaign object that we got: {campaign}")
                if not campaign:
                    logger.error(f"No campaign with this id")
                    return
                try:
                    logger.debug("Querying users with 'user' role")
                    users_with_role = session.query(extended_user).filter(extended_user.role=='user')
                    user_ids = [user.id for user in users_with_role]
                    total_users = len(user_ids)
                    logger.info(f"Attempting to send message to {total_users} users")
                    logger.info(f"Recipient list is {user_ids}")
                    for user in user_ids:
                        existing_record = (
                            session.query(UserMessage)
                            .filter_by(user_id=user, campaign_id=campaign.id)
                            .first()
                        )
                        if not existing_record:
                            new_record = UserMessage(user_id=user,campaign_id=campaign.id)
                            session.add(new_record)
                            session.commit()
                        
                    
                    
                    logger.info("message sent successfully")
                    
                    return Response({"message": "message sent successfully!", "Total users":total_users}, 
                                status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.error(f"Failed to send message: {str(e)}", exc_info=True)
                    return Response({"error": "Failed to send message"}, 
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            
        logger.warning(f"Invalid data provided: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
class UserCampaignViewSet(viewsets.ViewSet):
    """
    A viewset for viewing and creating user campaigns using SQLAlchemy.
    """
    permission_classes = [IsAuthenticated]
    def get_user_role(self):
        """Fetches user role"""
        user_id = self.request.user.id
        user_query = session.query(extended_user).filter_by(id=user_id).first()
        if not user_query:
            self.user_role="user"
        elif user_query.role=="admin":
            self.user_role="admin"
            self.user_role_data=user_query
        elif user_query.role=="superadmin":
            self.user_role="superadmin"
            self.user_role_data=user_query
        else:
            self.user_role="user"
            self.user_role_data=user_query
    
    def create(self, request, *args, **kwargs):
        self.get_user_role()
        logger.info("Received request to create new user campaign")
        logger.debug(f"Request data: {request.data}")
        created_by = request.user.id
        request.data['created_by']=created_by
        serializer = UserCampaignSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid campaign data provided: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
                logger.debug(f"serializer: {serializer}")
                user_campaign_data = serializer.validated_data
                logger.debug(f"Data from serializer: {serializer.validated_data}")
                logger.debug(f"Creating new campaign with data: {user_campaign_data}")
                # check_role = session.query(extended_user).filter_by(id=request.user.id).first()
                if self.user_role in ["superadmin", "admin"]:
                    new_campaign = UserCampaign(
                        type=user_campaign_data['type'],
                        text=user_campaign_data['text'],
                        description=user_campaign_data.get('description', ''),
                        created_by=user_campaign_data['created_by'],
                        status=user_campaign_data['status'],
                        admin_id= created_by if self.user_role=="admin" else None
                    )
                    session.add(new_campaign)
                    session.commit()
                    logger.info(f"Successfully created new campaign by user {created_by}")
                    
                    response_serializer = UserCampaignSerializer(new_campaign)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error":"You are not authorized to perform this action."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create campaign: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()
    def list(self, request, *args, **kwargs):
        logger.info("Received request to list all user campaigns")
        self.get_user_role()
        logger.info(f"Request role is {self.user_role}")
        try:
            campaigns = []
            if self.user_role=="superadmin":
                campaigns = session.query(UserCampaign).filter(UserCampaign.is_deleted==False).all()
            elif self.user_role=="admin":
                logger.info("Went to admin condition.")
                logger.info(f"user role practice_id is {self.user_role_data.practice_id}")
                admin_users = session.query(extended_user).filter(
                    extended_user.role=="admin",
                    extended_user.practice_id==self.user_role_data.practice_id
                ).all()
                logger.info(f"the admin user ids are {admin_users}")
                admin_practice_ids = [admin.id for admin in admin_users]
                logger.info(f"the admin user ids are {admin_practice_ids}")
                campaigns = session.query(UserCampaign).filter(
                    or_(UserCampaign.admin_id == None, UserCampaign.admin_id.in_(admin_practice_ids)),
                    UserCampaign.is_deleted==False
                ).all()
                logger.info(f"The length of campaigns are {len(campaigns)}")
            else:
                return Response({"error":"You are not authorized to perform this action."}, status=status.HTTP_401_UNAUTHORIZED)
            campaign_count = len(campaigns)
            logger.info(f"Successfully retrieved {campaign_count} campaigns")
            serializer = UserCampaignSerializer(campaigns, many=True)
            for idx, campaign_data in enumerate(serializer.data):
            # Add the admin_id from the original campaign object to the serialized data
                campaign_data['admin_id'] = campaigns[idx].admin_id if campaigns[idx].admin_id is not None else None

            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Failed to retrieve campaigns: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()
    def retrieve(self,request,pk=None, *args, **kwargs):
        self.get_user_role()
        try:
            if self.user_role in ["admin","superadmin"]:
                campaign = session.query(UserCampaign).filter(UserCampaign.id==pk).first()
                if campaign is None:
                    return Response({"detail": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND)
                serializer = UserCampaignSerializer(campaign)
                return Response(serializer.data)
            else:
                return Response({"error":"You are not authorized to perform this action."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Failed to retrieve campaign by ID {pk}: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close() 
    def update(self,request,pk=None, *args,**kwargs):
        
        self.get_user_role()
        try:
            campaign = session.query(UserCampaign).filter(UserCampaign.id==pk).first()
            if campaign is None:
                return Response({"detail": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND)
            request.data["created_by"]=request.user.id
            serializer = UserCampaignSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid campaign update data: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if self.user_role=="admin":
                if campaign.admin_id==None or campaign.admin_id!=request.user.id:
                    return Response({"error":"You are not authorized to perform this action."}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    campaign.type = request.data.get('type', campaign.type)
                    campaign.text = request.data.get('text', campaign.text)
                    campaign.description = request.data.get('description', campaign.description)
                    campaign.status = request.data.get('status', campaign.status)
                    campaign.created_by = request.user.id or campaign.created_by
                    session.commit()
                    response_serializer = UserCampaignSerializer(campaign)
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
            elif self.user_role=="superadmin":
                campaign.type = request.data.get('type', campaign.type)
                campaign.text = request.data.get('text', campaign.text)
                campaign.description = request.data.get('description', campaign.description)
                campaign.status = request.data.get('status', campaign.status)
                campaign.created_by = request.user.id or campaign.created_by
                # Commit the changes to the database
                session.commit()

                # Serialize the updated campaign and return the response
                response_serializer = UserCampaignSerializer(campaign)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update campaign {pk}: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()
            
        try:
            campaign = session.query(AdminUserCampaign).filter(AdminUserCampaign.id==pk).first()
            if campaign is None:
                return Response({"detail": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND)
            request.data["created_by"]=request.user.id
            serializer = UserCampaignSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid campaign update data: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            campaign.type = request.data.get('type', campaign.type)
            campaign.text = request.data.get('text', campaign.text)
            campaign.description = request.data.get('description', campaign.description)
            campaign.status = request.data.get('status', campaign.status)
            campaign.created_by = request.user.id or campaign.created_by
            # Commit the changes to the database
            session.commit()

            # Serialize the updated campaign and return the response
            response_serializer = UserCampaignSerializer(campaign)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update campaign {pk}: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()               
    def destroy(self, request, pk=None, *args, **kwargs):
        self.get_user_role()
        try:
            role = self.user_role
            campaign = session.query(UserCampaign).filter(UserCampaign.id == pk).first()
            logger.info(f"admin id of campaign is {campaign.admin_id}")
            if not campaign:
                logger.warning(f"Campaign with ID {pk} not found.")
                return Response({"message": "Campaign not found."}, status=status.HTTP_404_NOT_FOUND)

            if role == "superadmin":
                campaign.is_deleted = True
                logger.info(f"Superadmin deleted campaign ID {pk}")

            elif role == "admin":
                admin_users = session.query(extended_user).filter(
                    extended_user.role == "admin",
                    extended_user.practice_id == self.user_role_data.practice_id
                ).all()

                admin_practice_ids = [admin.id for admin in admin_users]
                logger.info(f"Admin user IDs: {admin_practice_ids}")
                logger.info(f"admin_id of campaign is {campaign.admin_id}")
                if campaign.admin_id not in admin_practice_ids:
                    logger.warning(f"Unauthorized delete attempt on campaign {pk} by admin {self.user_role_data.id}")
                    return Response({"message": "You are not authorized to perform this."}, status=status.HTTP_401_UNAUTHORIZED)

                campaign.is_deleted = True
                logger.info(f"Admin {self.user_role_data.id} deleted campaign ID {pk}")

            else:
                logger.warning(f"Unauthorized delete attempt on campaign {pk} by role {role}")
                return Response({"message": "You are not authorized to perform this."}, status=status.HTTP_401_UNAUTHORIZED)

            session.commit()
            return Response({"message": "Campaign deleted successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            session.rollback()
            logger.error(f"Error while deleting campaign ID {pk}: {str(e)}", exc_info=True)
            return Response({"message": "An error occurred while deleting the campaign."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            session.close()

                    
        
    
class MessageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def list(self, request):
        """
        List all messages for the authenticated user.
        """
        user_id = request.user.id
        logger.info(f"Fetching messages for user_id: {user_id}")
        try:
                messages = (
                    session.query(UserMessage)
                    .filter_by(user_id=user_id, is_selected=True)
                    .distinct()
                    .all()
                )
                logger.debug(f"Fetched {len(messages)} messages for user_id {user_id}")

                # Extract campaign IDs
                campaign_ids = [message.campaign_id for message in messages]
                logger.debug(f"Extracted campaign_ids: {campaign_ids}")

                # Query campaigns using campaign IDs
                campaigns = (
                    session.query(UserCampaign)
                    .filter(UserCampaign.id.in_(campaign_ids))
                    .all()
                )
                logger.info(f"Fetched {len(campaigns)} campaigns for user_id {user_id}")

                # Serialize the campaign data
                serializer = UserCampaignSerializer(campaigns, many=True)
                logger.info("Serialized campaign data successfully")

                return Response(serializer.data)

        except Exception as e:
            logger.error(f"An error occurred while fetching campaigns for user_id {user_id}: {e}")
            return Response(
                {"error": "An error occurred while processing your request."},
                status=500,
            )
    def update(self,request,pk=None):
        """Update a campaign by it's id"""
        user_id = request.user.id
        try:
            campaign = session.query(UserMessage).filter_by(campaign_id=pk).first()
            if not campaign:
                logger.warning(f"Campaign with ID {pk} not found for user_id {user_id}")
                return Response({"error":"Campain not found"},status=404)
            campaign.is_selected=False
            session.commit()
            logger.info(f"Successfully updated is_selected for campaign_id: {pk}")
            serializer = UserCampaignSerializer(campaign)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"An error occurred while updating campaign_id {pk}: {e}")
            session.rollback()  # Rollback transaction if an error occurs
            return Response(
                {"error": "An error occurred while processing your request."},
                status=500,
            )

class ScheduleCampaignViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    def create(self, request):
        logger.info("Received request to schedule the campaign")

        serializer = ScheduleCampaignSerializer(data=request.data)

        if serializer.is_valid():
            campaign_id = serializer.validated_data["campaign_id"]
            scheduled_date = serializer.validated_data["scheduled_date"]

            try:
                # Create new campaign sequence
                new_campaign_sequence = UserCampaignSequence(
                    user_campaign_id=campaign_id,
                    scheduled_date=scheduled_date,
                    status="pending",
                    created_by=request.user.id  # Assuming the user ID is available from the request
                )
                
                # Add to session and commit
                session.add(new_campaign_sequence)
                session.commit()
                
                # Log successful insertion
                logger.info(f"Successfully added campaign sequence with ID: {new_campaign_sequence.id}")
                
                # Return the newly created object as a response
                response_data = {
                    "campaign_id":new_campaign_sequence.user_campaign_id,
                    "scheduled_date": new_campaign_sequence.scheduled_date,
                }
                response_serializer = ScheduleCampaignSerializer(response_data)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            except SQLAlchemyError as e:
                # Log and handle database errors
                session.rollback()  # Rollback the transaction in case of error
                logger.error(f"Database error occurred while adding campaign sequence: {str(e)}")
                return Response({"error": "Database error occurred while scheduling campaign."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                # Log and handle other unexpected errors
                logger.error(f"Unexpected error occurred while adding campaign sequence: {str(e)}")
                return Response({"error": "Unexpected error occurred while scheduling campaign."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            # Log validation errors
            logger.error(f"Invalid data received for campaign scheduling: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SuperAdminSendCampaignViewSet(viewsets.ViewSet):
    # permission_classes=[IsAuthenticated, IsSuperAdmin]
    def create(self, request, *args, **kwargs):
        logger.info("Received request to send campaigns......................")
        serializer = SuperAdminSendCampaignSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid campaign data provided: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            practice_ids = serializer.validated_data["practice_ids"]
            campaign_id = serializer.validated_data["campaign_id"]
            logger.info(f"campaign_id is {campaign_id}")
            logger.info(f"practice_ids are {practice_ids}")
            # Corrected variable name
            user_ids = session.query(extended_user).filter(extended_user.practice_id.in_(practice_ids)).all()
            logger.info(f"user ids are {user_ids}")
            # Checking the correct variable
            if not user_ids:
                return Response({"message": "empty user id list."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Extracting the IDs from the query result
            user_ids = [user_id.id for user_id in user_ids]
            users_list = list(DjangoUser.objects.filter(id__in=user_ids).values_list('email', flat=True))
            total_users = len(users_list)   
            
            logger.info(f"Attempting to send email to {total_users} users")
            logger.info(f"Recipient list is {users_list}")
            
            campaign = session.query(UserCampaign).filter(UserCampaign.id==campaign_id).first()
            subject, message ="",""
            logger.info(f"campaign object that we got: {campaign}")
            if campaign:
                subject = campaign.text
                message = campaign.description
            send_email_task.apply_async(args=[subject, message, "anjulkushwaha11@gmail.com", users_list])
            logger.info("Email sent successfully")
            
            return Response({"message": "Email sent successfully!", "Total users": total_users}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return Response({"error": "Failed to send email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

         
            
        
