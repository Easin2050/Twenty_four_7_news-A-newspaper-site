from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from users.models import User, UserProfile
from users.serializers import UserSerializer,UserProfileSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, IsAuthenticated,IsAdminUser
from users.pagination import CustomPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,UpdateModelMixin
from api.permissions import IsProfileOwner
from drf_yasg.utils import swagger_auto_schema
 

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    http_method_names = ["get", "put", "patch"]  

    @swagger_auto_schema(
            operation_summary="User can create account using email"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return get_user_model().objects.all()
        return get_user_model().objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.request.method in ["GET", "PUT", "PATCH"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    
class UserProfileViewSet(GenericViewSet, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if UserProfile.objects.filter(user=self.request.user).exists():
            raise ValidationError({"detail": "Profile already exists."})
        serializer.save(user=self.request.user)

    
