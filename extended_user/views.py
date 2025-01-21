from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import extended_user
from .serializers import ExtendedUserSerializer, UserSerializer, LoginSerializer
from sqlalchemy import MetaData
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create handlers
file_handler = logging.FileHandler('user_management.log')
stream_handler = logging.StreamHandler()
# Create formatters and add it to handlers
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
stream_handler.setFormatter(log_format)
# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Create an SQLAlchemy engine and session to query extended_user
DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# views.py
class ExtendedUserViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        logger.info("Fetching all extended users")
        try:
            # Use SQLAlchemy to query extended_user table
            extended_users = session.query(extended_user).all()
            serializer = ExtendedUserSerializer(extended_users, many=True)
            logger.info(f"Successfully retrieved {len(extended_users)} extended users")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching extended users: {str(e)}")
            return Response({"error": "Failed to fetch users"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        logger.info("Attempting to create new user and extended user")
        # First create the Django User
        user_data = request.data
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            try:
                user = user_serializer.save()
                logger.info(f"Created Django user with ID: {user.id}")
                
                # Now create the extended_user in SQLAlchemy
                extended_user_data = {
                    'role': user_data['role'],
                    'id': user.id
                }
                new_extended_user = extended_user(**extended_user_data)
                session.add(new_extended_user)
                session.commit()
                logger.info(f"Created extended user with ID: {new_extended_user.id}")

                return Response({
                    "user_id": user.id,
                    "extended_user_id": new_extended_user.id,
                    "message": "User and extended user created successfully."
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating extended user: {str(e)}")
                # Attempt to rollback SQLAlchemy session
                session.rollback()
                # If Django user was created, attempt to delete it
                if 'user' in locals():
                    user.delete()
                    logger.info(f"Rolled back Django user creation for ID: {user.id}")
                return Response({"error": "Failed to create user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(f"Invalid user data: {user_serializer.errors}")
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        logger.info("Processing login request")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username', "")
            password = serializer.validated_data.get('password', "")
            logger.debug(f"Attempting authentication for user: {username}")
            
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                logger.info(f"Successful login for user: {username}")
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    "message": "Login successfull"
                })
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                return Response({
                    'message': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            logger.warning(f"Invalid login data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from .models import extended_user
# from .serializers import ExtendedUserSerializer, UserSerializer, LoginSerializer
# from sqlalchemy import MetaData

# # Create an SQLAlchemy engine and session to query extended_user
# DATABASE_URL = "postgresql://postgres:Anjul123@localhost:5432/lightbulb"
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
# session = Session()
# # views.py
# class ExtendedUserViewSet(viewsets.ViewSet):
#     def list(self, request, *args, **kwargs):
#         # Use SQLAlchemy to query extended_user table
#         extended_users = session.query(extended_user).all()
#         serializer = ExtendedUserSerializer(extended_users, many=True)
#         return Response(serializer.data)

#     def create(self, request, *args, **kwargs):
#         # First create the Django User
#         user_data = request.data
#         user_serializer = UserSerializer(data=user_data)
#         if user_serializer.is_valid():
#             user = user_serializer.save()
#             # Now create the extended_user in SQLAlchemy
#             extended_user_data = {
#                 'role': user_data['role'],
#                 'id': user.id
#             }
#             new_extended_user = extended_user(**extended_user_data)
#             session.add(new_extended_user)
#             session.commit()

#             return Response({
#                 "user_id": user.id,
#                 "extended_user_id": new_extended_user.id,
#                 "message": "User and extended user created successfully."
#             }, status=status.HTTP_201_CREATED)
#         else:
#             return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self,request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.validated_data.get('username',"")
#             password = serializer.validated_data.get('password',"")
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 refresh = RefreshToken.for_user(user)
#                 return Response({
#                     'refresh':str(refresh),
#                     'access': str(refresh.access_token),
#                     "message": "Login successfull"
#                 })
#             else:
#                 return Response({
#                     'message':'Invalid credentials'
#                 },status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        