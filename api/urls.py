from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserprofileViewSet
from users.views import UserViewSet
from news_app.views import NewsArticleViewSet,CategoryViewSet

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('categories',CategoryViewSet, basename='categories')
router.register('articles',NewsArticleViewSet, basename='articles')

userprofile_router = routers.NestedDefaultRouter(router, 'users', lookup='user')
userprofile_router.register('profiles', UserprofileViewSet, basename='user-profiles')

articles_router=routers.NestedDefaultRouter(router,'categories',lookup='category')
articles_router.register('articles',NewsArticleViewSet,basename='category-articles')

urlpatterns = [
    path('', include(router.urls)),             
    path('', include(userprofile_router.urls)), 
    path('', include(articles_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]