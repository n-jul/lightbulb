from rest_framework import serializers

class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255, required=True)
    message = serializers.CharField(required=True)
    from_email = serializers.EmailField(required=True)
    recipient_list = serializers.ListField(
        child=serializers.EmailField(), required=True
    )
