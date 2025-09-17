from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Avg
from news_app.models import NewsArticle,Category
from news_app.serializers import NewsArticleSerializer,CategorySerializer,ReviewSerializer,CategoryArticleSerializer
from users.pagination import CustomPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import IsAdminUser,AllowAny

class CategoryArticlesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategoryArticleSerializer
    lookup_field = 'category_id'

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return (
            NewsArticle.objects.filter(category_id=category_id)
            .annotate(avg_rating=Avg('ratings__value'))
            .order_by('-avg_rating', '-published_date')
        )
    
    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsAdminUser()]


class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset=NewsArticle.objects.all()
    serializer_class=NewsArticleSerializer
    pagination_class=CustomPagination


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.prefetch_related('ratings').all()
    serializer_class = ReviewSerializer


