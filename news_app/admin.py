from django.contrib import admin
from news_app.models import NewsArticle, Category, Rating

admin.site.register(NewsArticle)
admin.site.register(Category)
admin.site.register(Rating)