from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import CustomUserManager

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('subscriber', 'Subscriber/Viewer'),
        ('editor', 'Editor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='subscriber')
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='users/image/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"