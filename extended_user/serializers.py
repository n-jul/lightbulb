# serializers.py
from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth.models import User
# serializers.py
class SQLAlchemySerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        # This is a placeholder method for DRF compatibility
        pass

    def create(self, validated_data):
        # This is a placeholder method for DRF compatibility
        pass

    def to_representation(self, instance):
        """Convert SQLAlchemy object to a dictionary."""
        return {
            column.key: getattr(instance, column.key)
            for column in instance.__table__.columns
        }



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email']
        )
        # Hash the password before saving
        user.set_password(validated_data['password'])
        user.save()
        return user

# Custom serializer for SQLAlchemy model
from .models import extended_user
class ExtendedUserSerializer(SQLAlchemySerializer):
    class Meta:
        model = extended_user
        fields = ['id', 'role']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    