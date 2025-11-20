from rest_framework import serializers
from .models import Notification, UserFCMToken

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']


class UserFCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFCMToken
        fields = ['token']
