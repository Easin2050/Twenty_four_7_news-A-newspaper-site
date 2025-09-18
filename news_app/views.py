from django.shortcuts import render
from rest_framework import viewsets
from news_app.models import NewsArticle,Category
from news_app.serializers import NewsArticleSerializer,CategorySerializer,ReviewSerializer
from users.pagination import CustomPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import IsAdminUser,AllowAny

class CategoryViewSet(viewsets.ModelViewSet):
    queryset=Category.objects.prefetch_related('articles').all()
    serializer_class=CategorySerializer
    SearchFilter=['name']

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


