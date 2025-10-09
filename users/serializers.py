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
        read_only_fields=['role']
        

class UserProfileSerializer(serializers.ModelSerializer):
    profile_pic=serializers.ImageField()
    class Meta:
        model = UserProfile
        fields = ['id', 'bio', 'profile_pic', 'user']
        read_only_fields = ['user']

    def update(self, instance, validated_data):
        profile_pic = validated_data.get('profile_pic', None)
        if not profile_pic:
            validated_data['profile_pic'] = instance.profile_pic
        return super().update(instance, validated_data)