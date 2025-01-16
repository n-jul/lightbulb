from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from django.contrib.auth.models import User
from .models import extended_user
from .serializers import ExtendedUserSerializer, UserSerializer
from sqlalchemy import MetaData

# Create an SQLAlchemy engine and session to query extended_user
DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
# views.py
class ExtendedUserViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        # Use SQLAlchemy to query extended_user table
        extended_users = session.query(extended_user).all()
        serializer = ExtendedUserSerializer(extended_users, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # First create the Django User
        user_data = request.data
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            # Now create the extended_user in SQLAlchemy
            extended_user_data = {
                'role': user_data['role'],
                'id': user.id
            }
            new_extended_user = extended_user(**extended_user_data)
            session.add(new_extended_user)
            session.commit()

            return Response({
                "user_id": user.id,
                "extended_user_id": new_extended_user.id,
                "message": "User and extended user created successfully."
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
