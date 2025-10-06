from rest_framework import status,generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from users.models import User, UserProfile
from users.serializers import UserSerializer,UserProfileSerializer,UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, IsAuthenticated,IsAdminUser,AllowAny
from users.pagination import CustomPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,UpdateModelMixin
from api.permissions import IsProfileOwner
from drf_yasg.utils import swagger_auto_schema


from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerializer
from .pagination import CustomPagination

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    http_method_names = ["get", "put", "patch"]  

    def get_queryset(self):
        if self.request.user.is_superuser:
            return get_user_model().objects.all()
        return get_user_model().objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.request.method in ["GET", "PUT", "PATCH","POST"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        """
        Override create() to return only a success message after registration.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"message": "Account created successfully. Please verify your email if required."},
            status=status.HTTP_201_CREATED
        )


    
class UserProfileViewSet(GenericViewSet, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False):
            return UserProfile.objects.none()
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if UserProfile.objects.filter(user=self.request.user).exists():
            raise ValidationError({"detail": "Profile already exists."})
        serializer.save(user=self.request.user)
