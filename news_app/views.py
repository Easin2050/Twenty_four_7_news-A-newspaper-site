from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from news_app.models import NewsArticle,Category,Rating
from news_app.serializers import NewsArticleSerializer,CategorySerializer,ReviewSerializer,CategoryArticleSerializer,ArticleViewSerializer
from users.pagination import CustomPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import IsAdminUser,AllowAny
from api.permissions import IsAdminOrReadOnly,IsReviewOwnerOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset=Category.objects.prefetch_related('articles').all()
    serializer_class=CategorySerializer
    search_fields=['name']

    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsAdminOrReadOnly()]

class CategoryArticleViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryArticleSerializer
    permission_classes = [AllowAny]
    search_fields = ['title', 'body']
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self):
        category_id = self.kwargs.get('category_pk')
        return NewsArticle.objects.filter(category_id=category_id)

    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsAdminOrReadOnly()]

class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset=NewsArticle.objects.all()
    serializer_class=NewsArticleSerializer
    pagination_class=CustomPagination
    search_fields=['title','body']
    filter_backends=[SearchFilter,OrderingFilter]

    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsAdminOrReadOnly()]


class ArticleDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleViewSerializer
    search_fields = ['title']

    def get_queryset(self):
        article_id = self.kwargs.get('article_pk')
        return NewsArticle.objects.filter(id=article_id)

    @action(detail=True, methods=["get"])
    def with_related(self, request, pk=None, article_pk=None):
        article = self.get_object()
        related = (
            NewsArticle.objects.filter(category=article.category)
            .exclude(id=article.id)[:2]
        )
        data = {
            "article": ArticleViewSerializer(article).data,
            "Similiar news": [
                {"id": r.id, "title": r.title} for r in related
            ],
        }
        return Response(data)
    
    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsAdminOrReadOnly()]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewOwnerOrReadOnly]  

    def get_queryset(self):
        article_id = self.kwargs.get('article_pk')
        return Rating.objects.filter(article_id=article_id)

    def perform_create(self, serializer):
        article_id = self.kwargs.get('article_pk')
        serializer.save(
            user=self.request.user,   
            article_id=article_id    
        )


