from django.shortcuts import render
from rest_framework import viewsets
from users.models import User, UserProfile
from users.serializers import UserSerializer,UserProfileSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, IsAuthenticated,IsAdminUser
from users.pagination import CustomPagination

class UserViewSet(viewsets.ModelViewSet):
    queryset=get_user_model().objects.all()
    serializer_class=UserSerializer
    # permission_classes=[IsAuthenticated,IsAdminUser]
    pagination_class=CustomPagination

class UserprofileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    def get_queryset(self):
        return UserProfile.objects.filter(user_id=self.kwargs.get('user_pk'))