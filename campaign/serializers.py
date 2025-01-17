from rest_framework import serializers
from .models import UserCampaign

class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255, required=True)
    message = serializers.CharField(required=True)
    from_email = serializers.EmailField(required=True)
    recipient_list = serializers.ListField(
        child=serializers.EmailField(), required=True
    )



class UserCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCampaign
        fields = ['type', 'text', 'description', 'created_by']  # Exclude `status`, `created_at`, and `updated_at`

    def create(self, validated_data):
        # Ensure `status` is set to a default value if not provided
        validated_data['status'] = validated_data.get('status', 'active')  # Default status to 'active' if not provided
        validated_data['created_at'] = validated_data.get('created_at', None)  # Allow to be automatically set by DB
        validated_data['updated_at'] = validated_data.get('updated_at', None)  # Allow to be automatically set by DB

        return super().create(validated_data)

