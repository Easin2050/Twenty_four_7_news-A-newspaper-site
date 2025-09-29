from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Category(models.Model):
    name=models.CharField(max_length=100)
    description=models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class NewsArticle(models.Model):
    title=models.CharField(max_length=200)
    body=models.TextField()
    category=models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    published_date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}-{self.category}'

class Rating(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ratings = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])

    def __str__(self):
        return f'Rating {self.ratings} for {self.article.title} by {self.user.username}'
