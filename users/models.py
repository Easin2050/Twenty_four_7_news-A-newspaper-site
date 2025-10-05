from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import CustomUserManager
from uuid import uuid4

class User(AbstractUser):
    ROLE_CHOICES = (
        ('subscriber', 'Subscriber'),
        ('editor', 'Editor'),
    )
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='subscriber')

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email} - {self.role}'

class UserProfile(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='users/image/', blank=True, null=True)

    def __str__(self):    
        return f"Profile of {self.user.email}"

