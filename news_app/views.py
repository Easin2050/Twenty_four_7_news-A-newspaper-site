from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import viewsets
from news_app.models import NewsArticle,Category,NewsArticleImage,Rating
from news_app.serializers import NewsArticleSerializer,CategorySerializer,RatingSerializer,NewsArticleSerializer2,ArticleViewSerializer,HomepageArticleSerializer,NewsArticleImagesSerializer
from users.pagination import CustomPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.permissions import IsAdminUser,AllowAny,IsAuthenticated
from api.permissions import IsAdminOrReadOnly,IsReviewOwnerOrReadOnly,IsEditorOrReadOnly
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.db.models import Avg
from drf_yasg.utils import swagger_auto_schema


class CategoryViewSet(viewsets.ModelViewSet):
    queryset=Category.objects.prefetch_related('articles').all()
    serializer_class=CategorySerializer
    search_fields=['name']
    pagination_class=CustomPagination
    filter_backends=[SearchFilter,OrderingFilter]
    order_fields=['id','name']
    @swagger_auto_schema(
           operation_summary="Create a new category. Admins only.",
           operation_description="Create a new category with a unique name. Only admins can perform this action.",
           responses={201: CategorySerializer, 400: 'Bad Request'},
    )
    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError({"status": "Category with this name already exists."})
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
            operation_summary="Update an existing category. Admins only.",
            operation_description="Update the name of an existing category. Only admins can perform this action.",
            responses={200: CategorySerializer, 400: 'Bad Request', 404: 'Not Found'}
    )
    def update(self, request, *args, **kwargs):
        name = request.data.get('name')
        category_id = self.get_object().id
        if Category.objects.filter(name__iexact=name).exclude(id=category_id).exists():
            raise ValidationError({"status": "Category with this name already exists."})
        return super().update(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsAdminOrReadOnly()]
    
    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if category.articles.exists(): 
            raise ValidationError({"status": "Category with news cannot be deleted."})
        return super().destroy(request, *args, **kwargs)

    
class CategoryArticleViewSet(viewsets.ModelViewSet):
    serializer_class = NewsArticleSerializer2  
    search_fields = ['title', 'body']
    order_fields=['id','title']
    pagination_class = CustomPagination
    filter_backends = [SearchFilter,OrderingFilter]


    @swagger_auto_schema(
        operation_summary="List articles in a category (sorted by average rating)",
        operation_description=(
            "Retrieve a list of articles belonging to a specific category, "
            "ordered by their average rating (highest first). "
            "Each article includes its title and a short body preview (first 150 characters)."
        ),
        responses={200: NewsArticleSerializer2(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        category_id = self.kwargs.get('category_pk')
        return NewsArticle.objects.filter(category_id=category_id).annotate(
            rating=Avg('ratings__ratings')
        ).order_by('-rating')
    
    def perform_create(self, serializer):
        category_id = self.kwargs.get('category_pk')
        category = get_object_or_404(Category, pk=category_id)
        editor = self.request.user
        serializer.save(editor=editor, category=category)

    def perform_update(self, serializer):
        article = self.get_object()
        if not self.request.user.is_superuser and article.editor != self.request.user:
            raise ValidationError({"status": "You can only update your own articles."})
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser and instance.editor != self.request.user:
            raise ValidationError({"status": "You can only delete your own articles."})
        instance.delete()

    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsEditorOrReadOnly()]
    
class NewsArticleViewSet(viewsets.ModelViewSet):
    serializer_class=NewsArticleSerializer
    pagination_class=CustomPagination
    search_fields=['title','body']
    filter_backends=[SearchFilter,OrderingFilter]

    @swagger_auto_schema(
        operation_summary="List all news articles",
        operation_description="Retrieve all articles with optional search and ordering filters.",
        responses={200: NewsArticleSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    queryset = NewsArticle.objects.annotate(
        average_rating=Avg('ratings__ratings'),
    ).order_by('-published_date')

    def get_serializer_class(self):
        if self.action == 'retrieve':  
            return ArticleViewSerializer  
        return NewsArticleSerializer 

    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsEditorOrReadOnly()]

    def perform_create(self,serializer):
        editor=self.request.user
        serializer.save(editor=editor)

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.editor != self.request.user and not self.request.user.is_superuser:
            raise ValidationError({"status": "You can only update your own articles."})
        serializer.save()

    def perform_destroy(self, instance):
        if instance.editor != self.request.user and not self.request.user.is_superuser:
            raise ValidationError({"status": "You can only delete your own articles."})
        instance.delete()
    

class NewsArticleImageViewSet(viewsets.ModelViewSet):
    serializer_class = NewsArticleImagesSerializer
    permission_classes = [IsEditorOrReadOnly]

    def get_queryset(self):
        return NewsArticleImage.objects.filter(news_article_id=self.kwargs.get('article_pk'))

    def perform_create(self, serializer):
        article_id = self.kwargs.get('article_pk')
        article = get_object_or_404(NewsArticle, pk=article_id)

        if self.request.user != article.editor and not self.request.user.is_superuser:
            raise ValidationError({"status": "You do not have permission to add images to this article."})

        serializer.save(news_article=article)

    def perform_update(self, serializer):
        image = self.get_object()
        article = image.news_article

        if self.request.user != article.editor and not self.request.user.is_superuser:
            raise ValidationError({"status": "You do not have permission to edit images of this article."})

        serializer.save()

    def perform_destroy(self, instance):
        article = instance.news_article

        if self.request.user != article.editor and not self.request.user.is_superuser:
            raise ValidationError({"status": "You do not have permission to delete images of this article."})

        instance.delete()

        
class EditorsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsArticleSerializer
    permission_classes = [IsEditorOrReadOnly]
    search_fields = ['title', 'body']
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['published_date', 'title']
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return NewsArticle.objects.all()
        return NewsArticle.objects.filter(editor=user)

    def perform_create(self, serializer):
        serializer.save(editor=self.request.user)

class HomepageViewSet(viewsets.ModelViewSet):
    serializer_class= HomepageArticleSerializer
    search_fields=['title','body']
    queryset=NewsArticle.objects.all().order_by('-published_date')[:1]

    def get_permissions(self):
        if self.request.method=='GET':
            return [AllowAny()]
        return [IsAdminOrReadOnly()]

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [IsReviewOwnerOrReadOnly] 

    def get_queryset(self):
        article_id = self.kwargs.get('article_pk')
        user_id = self.kwargs.get('user_pk')

        if article_id:
            return Rating.objects.filter(article_id=article_id)
        elif user_id:
            return Rating.objects.filter(user_id=user_id)
        return Rating.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {
            'request': self.request,
            'article_id': self.kwargs.get('article_pk')
        }

    def perform_create(self, serializer):
        print("perform_create() called")

        article_id = self.kwargs.get('article_pk')
        article = get_object_or_404(NewsArticle, pk=article_id)
        author = article.editor
        user = self.request.user
        rating_value = self.request.data.get('ratings')

        print(f"Article ID: {article_id}, User: {user.username}, Rating: {rating_value}")

        rating, created = Rating.objects.update_or_create(
            article=article,
            user=user,
            defaults={'ratings': rating_value}
        )
        serializer.instance = rating

        print("Rating object created or updated:", "Created" if created else "Updated")

        subject_author = (
            f"New rating on your article '{article.title}'"
            if created else
            f"Rating updated for your article '{article.title}'"
        )
        message_author = (
            f"Hello {author.get_full_name() or author.username},\n\n"
            f"Your article '{article.title}' has "
            f"{'received a new' if created else 'been updated with a new'} rating.\n"
            f"User: {user.get_full_name() or user.username}\n"
            f"Rating: {rating_value} stars\n\n"
            "Best regards,\nTwenty Four 7 News"
        )

        subject_user = (
            f"Thank you for rating '{article.title}'"
            if created else
            f"Your rating for '{article.title}' has been updated"
        )
        message_user = (
            f"Hello {user.get_full_name() or user.username},\n\n"
            f"Thank you for {'rating' if created else 'updating your rating for'} "
            f"the article '{article.title}'.\n"
            f"Your rating: {rating_value} stars\n\n"
            "We appreciate your feedback!\nTwenty Four 7 News"
        )

        try:
            print("Attempting to send email to author...")
            if author and author.email:
                send_mail(
                    subject_author,
                    message_author,
                    settings.DEFAULT_FROM_EMAIL,
                    [author.email],
                    fail_silently=False
                )
                print("Email sent to author:", author.email)
            else:
                print("No author email found.")
        except Exception as e:
            print("Failed to send email to author:", e)

        try:
            print("Attempting to send email to user...")
            if user.email:
                send_mail(
                    subject_user,
                    message_user,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False
                )
                print("Email sent to user:", user.email)
            else:
                print("No user email found.")
        except Exception as e:
            print("Failed to send email to user:", e)

    def perform_update(self, serializer):
        print("perform_update() called")

        rating = serializer.save()
        user = self.request.user
        article = rating.article
        author = article.editor
        rating_value = rating.ratings

        print(f"Article ID: {article.id}, User: {user.username}, Updated Rating: {rating_value}")

        subject_author = f"Rating updated for your article '{article.title}'"
        message_author = (
            f"Hello {author.get_full_name() or author.username},\n\n"
            f"Your article '{article.title}' has been updated with a new rating.\n"
            f"User: {user.get_full_name() or user.username}\n"
            f"Rating: {rating_value} stars\n\n"
            "Best regards,\nTwenty Four 7 News"
        )

        subject_user = f"Your rating for '{article.title}' has been updated"
        message_user = (
            f"Hello {user.get_full_name() or user.username},\n\n"
            f"Thank you for updating your rating for the article '{article.title}'.\n"
            f"Your new rating: {rating_value} stars\n\n"
            "We appreciate your feedback!\nTwenty Four 7 News"
        )

        try:
            print("Attempting to send email to author...")
            if author and author.email:
                send_mail(
                    subject_author,
                    message_author,
                    settings.DEFAULT_FROM_EMAIL,
                    [author.email],
                    fail_silently=False
                )
                print("Email sent to author:", author.email)
            else:
                print("No author email found.")
        except Exception as e:
            print("Failed to send email to author:", e)

        try:
            print("Attempting to send email to user...")
            if user.email:
                send_mail(
                    subject_user,
                    message_user,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False
                )
                print("Email sent to user:", user.email)
            else:
                print("No user email found.")
        except Exception as e:
            print("Failed to send email to user:", e)




