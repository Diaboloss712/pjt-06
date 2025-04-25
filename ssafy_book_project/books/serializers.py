# books/serializers.py
from rest_framework import serializers
from .models import Category, Book


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  



class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # Category를 포함한 중첩 시리얼라이저

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'customer_review_rank', 'author',
            'author_profile_img', 'author_info', 'author_works', 'cover_image',
            'audio_file', 'user_id', 'isbn', 'category'
        ]

