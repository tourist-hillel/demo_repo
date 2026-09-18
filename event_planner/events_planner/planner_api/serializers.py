from rest_framework import serializers
from django.contrib.auth import get_user_model
from events.models import Event
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'cell_phone', 'date_of_birth', 'first_name', 'last_name', 'app_lang']
        read_only_fields = ['id']


class EventSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True), source='user', write_only=True
    )
    is_overdue = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'strat_time', 'end_date', 'user', 'user_id', 'created_at', 'is_completed', 'is_overdue', 'duration']
        read_only_fields = ['id', 'created_at', 'user', 'is_overdue', 'duration']

    def get_is_overdue(self, obj):
        if not obj.is_completed and obj.end_date:
            return obj.end_date < timezone.now()
        return False

    def get_duration(self, obj):
        if obj.strat_time and obj.end_date:
            delta = obj.end_date - obj.strat_time
            hours = delta.total_seconds() // 3600
            minutes = (delta.total_seconds() % 3600) // 60
            return f'{int(hours)}h, {int(minutes)}m'
        return None

    def validate(self, attrs):
        start_date = attrs.get('strat_time')
        end_date = attrs.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError('End date cannot be set beyond the start date')
        if end_date and end_date < timezone.now():
            raise serializers.ValidationError('End date cannot be in the past')
        return attrs

    def create(self, validated_data):
        validated_data['title'] = validated_data['title'] + "added from 'create()' method"
        return super().create(validated_data)