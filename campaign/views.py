from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.models import User as DjangoUser
from .serializers import EmailSerializer

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from extended_user.models import extended_user
DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

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
