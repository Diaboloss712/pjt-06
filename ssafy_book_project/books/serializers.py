from rest_framework import serializers
from .models import Book, Thread, Comment


class ThreadTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('title',)


class BookTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title',)


class CommentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'updated_at',)
    thread = ThreadTitleSerializer(read_only=True)


class ThreadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('id', 'title')
    book = BookTitleSerializer(read_only=True)


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('id', 'title')
    book = BookTitleSerializer(read_only=True)
    comments = CommentDetailSerializer(read_only=True, many=True)

    num_of_comments = serializers.SerializerMethodField()

    def get_num_of_comments(self, obj):
        return obj.num_of_comments


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id','content','created_at','updated_at',)
    book = BookTitleSerializer(read_only=True, source='thread_id.book_id')
    
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

