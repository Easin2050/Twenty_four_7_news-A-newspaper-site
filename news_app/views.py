from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from news_app.models import NewsArticle,Category,Rating
from news_app.serializers import NewsArticleSerializer,CategorySerializer,ReviewSerializer,CategoryArticleSerializer,ArticleViewSerializer
from users.pagination import CustomPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import IsAdminUser,AllowAny
from api.permissions import IsAdminOrReadOnly,IsReviewOwnerOrReadOnly,IsEditorOrReadOnly
from django.core.mail import send_mail
from django.conf import settings

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
        return [IsEditorOrReadOnly()]

    def perform_create(self,serializer):
        editor=self.request.user
        serializer.save(editor=editor)

    def perform_update(self, serializer):
        if self.get_object().editor != self.request.user:
            raise ValueError("You can only update your own articles.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.editor != self.request.user:
            raise ValueError("You can only delete your own articles.")
        instance.delete()


class EditorsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsArticleSerializer
    permission_classes = [IsEditorOrReadOnly]
    search_fields = ['title', 'body']
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self):
        editor_id=self.request.user.id
        return NewsArticle.objects.filter(editor_id=editor_id)

    def perform_create(self,serializer):
        editor=self.request.user
        serializer.save(editor=editor)


class ArticleDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleViewSerializer
    search_fields = ['title']

    def get_queryset(self):
        article_id = self.kwargs.get('article_pk')
        return NewsArticle.objects.filter(id=article_id)

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

        if Rating.objects.filter(article_id=article_id, user=self.request.user).exists():
            raise ValueError("You have already reviewed this article.")

        review = serializer.save(
            user=self.request.user,
            article_id=article_id
        )

        article = review.article  
        subject = f"New rating for your article: {article.title}"
        message = f"Your article '{article.title}' received a rating of {review.value} from {self.request.user.email}."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [article.editor.email]  

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)



