from rest_framework import serializers
from .models import NewsArticle, Category,Rating,NewsArticleImage
from django.db.models import Avg

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
        return obj.body[:50]+'...' if obj.body else ''


class ArticleViewSerializer(serializers.ModelSerializer):
    related_articles = serializers.SerializerMethodField(method_name='get_related_articles')
    class Meta:
        model=NewsArticle
        fields=['id','title','body','related_articles']

    def get_related_articles(self, obj):
        related = NewsArticle.objects.filter(category=obj.category).exclude(id=obj.id)[:2]
        return [{"id": r.id, "title": r.title} for r in related]


class RatingSerializer(serializers.ModelSerializer):
    average_ratings=serializers.SerializerMethodField(method_name='get_average_rating')
    
    class Meta:
        model = Rating
        fields = ['id', 'article', 'user', 'average_ratings', 'ratings']
        read_only_fields = ['user','article']

    def get_average_rating(self, obj):
        avg = obj.article.ratings.aggregate(avg=Avg("ratings"))["avg"]
        return round(avg, 2) if avg is not None else None