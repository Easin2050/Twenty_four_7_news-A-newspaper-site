from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserProfileViewSet
from users.views import UserViewSet
from news_app.views import NewsArticleViewSet,CategoryViewSet,CategoryArticleViewSet,RatingViewSet,EditorsViewSet,HomepageViewSet,NewsArticleImageViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categories')
router.register('articles', NewsArticleViewSet, basename='articles')
router.register('profiles', UserProfileViewSet, basename='profiles')
router.register('editors', EditorsViewSet, basename='editors')
router.register('homepage', HomepageViewSet, basename='homepage')

userprofile_router = routers.NestedDefaultRouter(router, 'users', lookup='user')
userprofile_router.register('profiles', UserProfileViewSet, basename='user-profiles')

articles_router = routers.NestedDefaultRouter(router, 'categories', lookup='category')
articles_router.register('articles', CategoryArticleViewSet, basename='category-articles')

article_details_router = routers.NestedDefaultRouter(router, 'articles', lookup='article')
article_details_router.register('details', NewsArticleViewSet, basename='article-details')
article_details_router.register('images', NewsArticleImageViewSet, basename='images')

articles_rating_router = routers.NestedDefaultRouter(router, 'articles', lookup='article')
articles_rating_router.register('ratings', RatingViewSet, basename='article-ratings')

editors_router = routers.NestedDefaultRouter(router, 'editors', lookup='editor')
editors_router.register('articles', EditorsViewSet, basename='editor-articles')

users_router = routers.NestedSimpleRouter(router, 'users', lookup='user')
users_router.register('ratings', RatingViewSet, basename='user-ratings')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(userprofile_router.urls)),
    path('', include(articles_router.urls)),
    path('', include(article_details_router.urls)),
    path('', include(articles_rating_router.urls)),  
    path('', include(editors_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]