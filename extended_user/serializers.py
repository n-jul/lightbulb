# serializers.py
from rest_framework import serializers
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


# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

# Custom serializer for SQLAlchemy model
from .models import extended_user
class ExtendedUserSerializer(SQLAlchemySerializer):
    class Meta:
        model = extended_user
        fields = ['id', 'role']
