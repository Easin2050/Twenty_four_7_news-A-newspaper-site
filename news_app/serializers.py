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


'''class NewsArticleImagesSerializer(serializers.ModelSerializer):
    image=serializers.ImageField()
    class Meta:
        model=NewsArticleImage
        fields=['id','image']
        
    def get_image(self, obj):
        try:
            return obj.image.url  
        except Exception:
            return str(obj.image) '''

class NewsArticleImagesSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    http_method_names = ['get', 'patch']
    class Meta:
        model = NewsArticleImage
        fields = ['id', 'image']

    def get_image(self, obj):
        try:
            return obj.image.url
        except Exception:
            return str(obj.image) 

    
class NewsArticleSerializer(serializers.ModelSerializer):
    average_ratings = serializers.SerializerMethodField()
    images = NewsArticleImagesSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'body', 'category', 'category_name', 'published_date', 'images', 'average_ratings']
        read_only_fields = ['average_ratings']

    def get_average_ratings(self, obj):
        avg = obj.ratings.aggregate(avg=Avg("ratings"))["avg"]
        return round(avg, 2) if avg is not None else 0

class NewsArticleSerializer2(serializers.ModelSerializer):
    short_body = serializers.SerializerMethodField(method_name='short_body_method')
    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'short_body']

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
        return NewsArticleSerializer2(obj.article).data

    def create(self, validated_data):
        article_id = self.context['article_id']
        user = self.context['request'].user
        rating_value = validated_data.get('ratings')
        rating = Rating.objects.create(
            article_id=article_id,
            user=user,
            ratings=rating_value
        )
        return rating
