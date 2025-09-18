from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from users.models import User, UserProfile
from users.serializers import UserSerializer,UserProfileSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, IsAuthenticated,IsAdminUser
from users.pagination import CustomPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,UpdateModelMixin
from api.permissions import IsProfileOwner

class UserViewSet(ModelViewSet):
    serializer_class=UserSerializer
    pagination_class=CustomPagination
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return get_user_model().objects.all()
        return get_user_model().objects.filter(id=self.request.user.id)


class UserProfileViewSet(GenericViewSet, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Profile already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)
