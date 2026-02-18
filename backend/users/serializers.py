from django.contrib.auth import get_user_model
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    last_log = serializers.DateTimeField(source='last_login', read_only=True)
    
    class Meta:
        model = get_user_model()
        fields = '__all__'


class UserUpdateSerializer(serializers.ModelSerializer):
    last_log = serializers.DateTimeField(source='last_login', read_only=True)
    
    class Meta:
        model = get_user_model()
        fields = '__all__'
    
    def validate_email(self, email):
        if email:
            # Check if another user already has this email
            existing_user = User.objects.filter(email=email).exclude(id=self.instance.id if self.instance else None).first()
            if existing_user:
                raise serializers.ValidationError("A user with this email already exists.")
        return email
    
    def validate_username(self, username):
        if username:
            # Check if another user already has this username
            existing_user = User.objects.filter(username=username).exclude(id=self.instance.id if self.instance else None).first()
            if existing_user:
                raise serializers.ValidationError("A user with this username already exists.")
        return username


class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)

    def validate_email(self, email):
        if email:
            if User.objects.filter(email=email).exists():
                raise ValidationError("A user with this email already exists.")
        return email

    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save()

        groups = self.validated_data.get('groups', [])
        user.groups.set(groups)

        return user