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
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,ListModelMixin
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from api.permissions import IsProfileOwnerOrAdmin

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    http_method_names = ["get", "put", "patch"]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return get_user_model().objects.all()
        return get_user_model().objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.request.method in ["GET", "PUT", "PATCH"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    


class UserProfileViewSet(GenericViewSet, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin,ListModelMixin):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserProfile.objects.none()

        user = self.request.user
        if user.is_superuser:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        if not self.request.user.is_superuser and UserProfile.objects.filter(user=self.request.user).exists():
            raise ValidationError({"status": "You already have a profile."})
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        profile = self.get_object()

        if not self.request.user.is_superuser and profile.user != self.request.user:
            raise ValidationError({"status": "You can only update your own profile."})

        if 'profile_pic' not in self.request.data or not self.request.data.get('profile_pic'):
            serializer.validated_data['profile_pic'] = profile.profile_pic

        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser and instance.user != self.request.user:
            raise ValidationError({"status": "You can only delete your own profile."})
        instance.delete()

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """Endpoint for user to get or update their own profile"""
        profile = get_object_or_404(UserProfile, user=request.user)

        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
