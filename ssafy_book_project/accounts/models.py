# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# 사용자 모델을 관리할 UserManager 작성
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """일반 사용자 생성"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # 비밀번호 해싱
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """슈퍼유저 생성"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

# 사용자 모델 정의
class User(AbstractUser):
    # 팔로우 유저 정보를 저장하는 필드 (Many-to-Many 관계)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    objects = CustomUserManager()  # 사용자 모델에 CustomUserManager 연결

    def __str__(self):
        return self.username
