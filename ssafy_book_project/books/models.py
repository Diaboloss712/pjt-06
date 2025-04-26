from django.db import models
from accounts.models import User
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=20)
    description = models.TextField()
    customer_review_rank = models.IntegerField()
    author = models.CharField(max_length=15)
    author_profile_img = models.ImageField(upload_to="author_profiles/", blank=True)
    author_info = models.TextField()
    author_works = models.CharField(max_length=50)
    cover_image = models.ImageField(blank=True)
    audio_file = models.FileField(upload_to="tts/", blank=True, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    # Category와의 관계 추가 (ForeignKey)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class Thread(models.Model):
    book_id = models.ForeignKey(Book, related_name='threads', on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    content = models.TextField()
    reading_date = models.DateField()
    cover_img = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_threads', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='threads')


class Comment(models.Model):
    thread_id = models.ForeignKey(Thread, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='comments')
