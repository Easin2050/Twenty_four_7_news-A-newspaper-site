from django.shortcuts import render
from rest_framework import viewsets
from news_app.models import NewsArticle,Category
from news_app.serializers import NewsArticleSerializer,CategorySerializer,ReviewSerializer
from users.pagination import CustomPagination

class CategoryViewSet(viewsets.ModelViewSet):
    queryset=Category.objects.prefetch_related('articles').all()
    serializer_class=CategorySerializer

class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset=NewsArticle.objects.all()
    serializer_class=NewsArticleSerializer
    pagination_class=CustomPagination

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.prefetch_related('ratings').all()
    serializer_class = ReviewSerializer


