from rest_framework import serializers
from .models import NewsArticle, Category,Rating

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','description']

class CategoryArticleSerializer(serializers.ModelSerializer):
    short_body = serializers.SerializerMethodField(method_name='short_body_method')
    related_articles = serializers.SerializerMethodField(method_name='get_related_articles')

    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'short_body','related_articles']

    def short_body_method(self, obj):
        return obj.body[:150] 

    def get_related_articles(self, obj):
        related = NewsArticle.objects.filter(category=obj.category).exclude(id=obj.id)[:2]
        return [{"id": r.id, "title": r.title} for r in related]

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model=NewsArticle
        fields=['id','title','body','category','published_date']


class ArticleViewSerializer(serializers.ModelSerializer):
    class Meta:
        model=NewsArticle
        fields=['id','title','body']



class ReviewSerializer(serializers.ModelSerializer):
    average_ratings=serializers.SerializerMethodField(method_name='show_average_ratings')
    
    class Meta:
        model = Rating
        fields = ['id', 'article', 'user', 'average_ratings', 'ratings']
        read_only_fields = ['user','article']

    def show_average_ratings(self, obj):
        reviews = obj.ratings.all()
        if reviews.exists():
            return sum([review.ratings for review in reviews]) / reviews.count()
        return 0