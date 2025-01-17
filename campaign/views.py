from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.models import User as DjangoUser
from .serializers import EmailSerializer

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import UserCampaign
from .serializers import UserCampaignSerializer

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from extended_user.models import extended_user
DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Session = sessionmaker(bind=engine)

def check_if_superadmin(user_id):
    """
    Checks if a given user ID exists in the database and if their role is 'superadmin'.
    Returns True if user exists and is a superadmin, otherwise False.
    """
    # session = Session()
    try:
        # Query the database to check if the user exists
        user = session.query(extended_user).filter_by(id=user_id).first()
        
        # Check if the user exists and has 'superadmin' role
        if user and user.role == 'superadmin':
            return True
        return False
        
    except Exception as e:
        print(f"Error checking user role: {str(e)}")
        return False
    finally:
        session.close()


class SendTestEmailViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for sending test emails.
    """
    def create(self, request):
        # Deserialize the input data using the EmailSerializer
        serializer = EmailSerializer(data=request.data)

        # Validate the data
        if serializer.is_valid():
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            from_email = serializer.validated_data['from_email']
            recipient_list = serializer.validated_data['recipient_list']
            users_with_role = session.query(extended_user).filter(extended_user.role=='user')
            user_ids = [user.id for user in users_with_role]
            # Send the email
            users_list = DjangoUser.objects.filter(id__in=user_ids).values_list('email', flat=True)
            total_users = len(users_list)
            send_mail(subject, message, from_email, users_list)

            # Return success message
            return Response({"message": "Email sent successfully!", "Total users":total_users}, status=status.HTTP_201_CREATED)
        
        # If the data is invalid, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCampaignViewSet(viewsets.ViewSet):
    """
    A viewset for viewing and creating user campaigns using SQLAlchemy.
    """
    def create(self, request, *args, **kwargs):
        """
        Override the create method to automatically add the logged-in user as `created_by`.
        """
        user_id=request.data.get('created_by',None)
        if not user_id:
            return Response({'error': "No user ID provided."}, status=status.HTTP_400_BAD_REQUEST)
        if not check_if_superadmin(user_id):
            return Response({'error': "You don't have the permission to create the campaign..."})
        # Validate the incoming data using the serializer
        serializer = UserCampaignSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Prepare the data and add created_by (logged-in user)
                user_campaign_data = serializer.validated_data
                # user_campaign_data['created_by'] = request.user.id  # Adding logged-in user

                # Create the new UserCampaign object
                new_campaign = UserCampaign(
                    type=user_campaign_data['type'],
                    text=user_campaign_data['text'],
                    description=user_campaign_data.get('description', ''),
                    created_by=user_campaign_data['created_by'],
                    status=user_campaign_data['status'],
                )
                session.add(new_campaign)
                session.commit()
                # Serialize and return the newly created campaign
                response_serializer = UserCampaignSerializer(new_campaign)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                session.rollback()  # Rollback in case of any error
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            finally:
                session.close()
        else:
            # If the serializer is invalid, return errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request, *args, **kwargs):
        """
        Override the list method to retrieve all user campaigns using SQLAlchemy.
        """
        try:
            campaigns = session.query(UserCampaign).all()
            serializer = UserCampaignSerializer(campaigns, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            session.close()