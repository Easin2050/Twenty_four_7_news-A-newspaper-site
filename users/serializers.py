from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import User,UserProfile
from django.contrib.auth import get_user_model

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        ref_name = "CustomUser" 
        fields = ['id', 'email', 'password', 'first_name',
                  'last_name']

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        ref_name = "CustomUserCreate" 
        fields = ['id', 'email', 'first_name',
                  'last_name','role']
        

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields=['id','bio','profile_pic']

    def create(self, validated_data):
        user = self.context['request'].user
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile