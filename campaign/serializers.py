import logging
from rest_framework import serializers
from .models import UserCampaign
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from django.utils.timezone import make_aware, is_aware
logger = logging.getLogger(__name__)

class SQLAlchemySerializer(serializers.Serializer):
    session: Session
    def update(self, instance, validated_data):
        # Placeholder method for DRF compatibility
        pass

    def create(self, validated_data):
        """
        Create an instance of the model using the validated data.
        """
        model_class = self.Meta.model
        instance = model_class(**validated_data)
        self.session.add(instance)
        self.session.commit()
        return instance

    def to_representation(self, instance):
        """Convert SQLAlchemy object to a dictionary."""
        representation = {
            column.key: getattr(instance, column.key)
            for column in instance.__table__.columns
        }
        logger.debug(f"to_representation output: {representation}")
        return representation
    @property
    def errors(self):
        return self._errors
class EmailSerializer(serializers.Serializer):
    on_email = serializers.BooleanField(default=True)
    campaign_id = serializers.IntegerField(required=True)
    send_now = serializers.BooleanField(default=True)
    scheduled_time = serializers.DateTimeField(required=False, allow_null=True)
    
class ScheduleCampaignSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField(required=True)    
    scheduled_date = serializers.DateTimeField(required=True)   

class UserCampaignSerializer(SQLAlchemySerializer):
    type = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    
    # status will default to 'active' if not provided
    status = serializers.CharField(default='pending', required=False)
    
    # created_at and updated_at will be populated by the database, so they are read-only
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    # created_by is required and should be an integer (user ID)
    created_by = serializers.IntegerField(required=True)

    def create(self, validated_data):
        logger.debug(f"Validated data before setting defaults: {validated_data}")
        
        # Ensure `status` is set to a default value if not provided
        validated_data['status'] = validated_data.get('status', 'active')
        validated_data['created_at'] = validated_data.get('created_at', None)  # Allow to be automatically set by DB
        validated_data['updated_at'] = validated_data.get('updated_at', None)  # Allow to be automatically set by DB

        logger.debug(f"Validated data after setting defaults: {validated_data}")
        
        try:
            instance = super().create(validated_data)
            logger.info(f"Successfully created UserCampaign instance: {instance}")
            return instance
        except Exception as e:
            logger.error(f"Error creating UserCampaign instance: {e}", exc_info=True)
            raise




# from rest_framework import serializers
# from .models import UserCampaign

# class SQLAlchemySerializer(serializers.Serializer):
#     def update(self, instance, validated_data):
#         # This is a placeholder method for DRF compatibility
#         pass

#     def create(self, validated_data):
#         # This is a placeholder method for DRF compatibility
#         pass

#     def to_representation(self, instance):
#         """Convert SQLAlchemy object to a dictionary."""
#         return {
#             column.key: getattr(instance, column.key)
#             for column in instance.__table__.columns
#         }


# class EmailSerializer(serializers.Serializer):
#     subject = serializers.CharField(max_length=255, required=True)
#     message = serializers.CharField(required=True)
#     from_email = serializers.EmailField(required=True)
#     recipient_list = serializers.ListField(
#         child=serializers.EmailField(), required=True
#     )



# class UserCampaignSerializer(SQLAlchemySerializer):
#     class Meta:
#         model = UserCampaign
#         fields = ['type', 'text', 'description', 'created_by']  # Exclude `status`, `created_at`, and `updated_at`

#     def create(self, validated_data):
#         # Ensure `status` is set to a default value if not provided
#         validated_data['status'] = validated_data.get('status', 'active')  # Default status to 'active' if not provided
#         validated_data['created_at'] = validated_data.get('created_at', None)  # Allow to be automatically set by DB
#         validated_data['updated_at'] = validated_data.get('updated_at', None)  # Allow to be automatically set by DB

#         return super().create(validated_data)

