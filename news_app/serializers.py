from rest_framework import serializers
from .models import NewsArticle, Category,Rating,NewsArticleImage
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','description']


class NewsArticleImagesSerializer(serializers.ModelSerializer):
    image=serializers.ImageField()
    class Meta:
        model=NewsArticleImage
        fields=['id','image']

class NewsArticleSerializer(serializers.ModelSerializer):
    average_ratings=serializers.SerializerMethodField(method_name='get_average_ratings')
    images=NewsArticleImagesSerializer(many=True,read_only=True)
    category = serializers.SerializerMethodField(method_name='get_category')
    class Meta:
        model=NewsArticle
        fields = ['id', 'title', 'body', 'category', 'published_date','images', 'average_ratings']
        read_only_fields=['average_ratings']
    
    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_average_ratings(self, obj):
        avg = obj.ratings.aggregate(avg=Avg("ratings"))["avg"]
        return round(avg, 2) if avg is not None else None
    

class NewsArticleSerializer2(serializers.ModelSerializer):
    short_body = serializers.SerializerMethodField(method_name='short_body_method')
    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'short_body',]

    def short_body_method(self, obj):
        return obj.body[:150] + '...' if obj.body else ''

class HomepageArticleSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField(method_name='short_body_method')

    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'body']

    def short_body_method(self, obj):
        return obj.body[:50] + '...' if obj.body else ''


class ArticleViewSerializer(serializers.ModelSerializer):
    related_articles = serializers.SerializerMethodField(method_name='get_related_articles')
    class Meta:
        model=NewsArticle
        fields=['id','title','body','related_articles']

    def get_related_articles(self, obj):
        related = NewsArticle.objects.filter(category=obj.category).exclude(id=obj.id)[:2]
        return [{"id": r.id, "title": r.title} for r in related]

class SimpleUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'full_name']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email  

'''class RatingSerializer(serializers.ModelSerializer):
    user= serializers.SerializerMethodField(method_name='get_user')
    article = serializers.SerializerMethodField(method_name='get_article_details')

    class Meta:
        model = Rating
        fields = ['id', 'article', 'user', 'ratings']
        read_only_fields = ['user', 'article']

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    def get_article_details(self, obj):
        return NewsArticleSerializer2(obj.article).data

    def create(self, validated_data):
        news_id = self.context['article_id']
        return Rating.objects.create(article_id=news_id, **validated_data)'''

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name='get_user')
    article = serializers.SerializerMethodField(method_name='get_article')

    class Meta:
        model = Rating
        fields = ['id', 'article', 'user', 'ratings']
        read_only_fields = ['user', 'article']

    def get_user(self, obj):
        return SimpleUserSerializer(obj.user).data

    def get_article(self, obj):
        from news_app.serializers import NewsArticleSerializer2
        return NewsArticleSerializer2(obj.article).data

    def create(self, validated_data):
        article_id = self.context['article_id']
        user = self.context['request'].user
        rating_value = validated_data.get('ratings')

        article = get_object_or_404(NewsArticle, id=article_id)
        author = article.editor

        rating, created = Rating.objects.update_or_create(
            article=article,
            user=user,
            defaults={'ratings': rating_value}
        )

        if author and author.email:
            send_mail(
                subject=f"New rating on your article '{article.title}'",
                message=(
                    f"Hello {author.get_full_name()},\n\n"
                    f"Your article '{article.title}' has received a new rating.\n"
                    f"User: {user.get_full_name()}\n"
                    f"Rating: {rating_value} stars\n\n"
                    "Best regards,\nTwenty Four 7 News"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[author.email],
                fail_silently=True,
            )

        if user and user.email:
            send_mail(
                subject=f"Thank you for rating '{article.title}'",
                message=(
                    f"Hello {user.get_full_name()},\n\n"
                    f"Thank you for rating the article '{article.title}'.\n"
                    f"Your rating: {rating_value} stars\n\n"
                    "We appreciate your feedback!\nTwenty Four 7 News"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

        return rating

    def update(self, instance, validated_data):
        instance.ratings = validated_data.get('ratings', instance.ratings)
        instance.save()

        user = instance.user
        article = instance.article
        author = article.editor

        if author and author.email:
            send_mail(
                subject=f"Updated rating on your article '{article.title}'",
                message=(
                    f"Hello {author.get_full_name()},\n\n"
                    f"User {user.get_full_name()} updated their rating.\n"
                    f"New Rating: {instance.ratings} stars\n\n"
                    "Best regards,\nTwenty Four 7 News"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[author.email],
                fail_silently=True,
            )

        if user and user.email:
            send_mail(
                subject=f"Your rating updated for '{article.title}'",
                message=(
                    f"Hello {user.get_full_name()},\n\n"
                    f"You updated your rating for article '{article.title}'.\n"
                    f"New Rating: {instance.ratings} stars\n\n"
                    "We appreciate your feedback!\nTwenty Four 7 News"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

        return instance