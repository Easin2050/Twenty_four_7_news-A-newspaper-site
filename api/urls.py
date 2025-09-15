from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserprofileViewSet
from users.views import UserViewSet

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')

userprofile_router = routers.NestedDefaultRouter(router, 'users', lookup='user')
userprofile_router.register('profiles', UserprofileViewSet, basename='user-profiles')

urlpatterns = [
    path('', include(router.urls)),             
    path('', include(userprofile_router.urls)), 
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]