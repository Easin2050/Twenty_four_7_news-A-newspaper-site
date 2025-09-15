from rest_framework import serializers
from .models import NewsArticle, Category,Rating

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','description']


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model=NewsArticle
        fields=['title','body','category','published_date']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'article', 'user', 'value']