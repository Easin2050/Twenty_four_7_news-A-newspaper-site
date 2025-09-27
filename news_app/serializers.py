from rest_framework import serializers
from .models import NewsArticle, Category,Rating

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','description']

class CategoryArticleSerializer(serializers.ModelSerializer):
    short_body = serializers.SerializerMethodField(method_name='short_body_method')

    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'short_body']

    def short_body_method(self, obj):
        return obj.body[:50] 

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model=NewsArticle
        fields=['id','title','body','category','published_date']


class ArticleViewSerializer(serializers.ModelSerializer):
    class Meta:
        model=NewsArticle
        fields=['id','title','body']



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'article', 'user', 'value']