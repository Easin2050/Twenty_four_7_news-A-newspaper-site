from django.shortcuts import render
from rest_framework import viewsets
from users.models import User, UserProfile
from users.serializers import UserSerializer,UserProfileSerializer
from django.contrib.auth import get_user_model

class UserViewSet(viewsets.ModelViewSet):
    queryset=get_user_model().objects.all()
    serializer_class=UserSerializer


class UserprofileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    def get_queryset(self):
        return UserProfile.objects.filter(user_id=self.kwargs.get('user_pk'))