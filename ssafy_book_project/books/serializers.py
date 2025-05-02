from rest_framework import serializers
from .models import Book, Thread, Category, Comment
from drf_spectacular.utils import extend_schema_field

class BookTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title',)

class ThreadTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('title',)

class CommentDetailSerializer(serializers.ModelSerializer):
    thread = ThreadTitleSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'updated_at', 'thread')

class ThreadListSerializer(serializers.ModelSerializer):
    book = BookTitleSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'book')

@extend_schema_field(serializers.IntegerField())
class ThreadSerializer(serializers.ModelSerializer):
    book = BookTitleSerializer(read_only=True)
    comments = CommentDetailSerializer(many=True, read_only=True)
    num_of_comments = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ('id', 'title', 'content', 'book', 'comments', 'num_of_comments')

    def get_num_of_comments(self, obj):
        return getattr(obj, 'num_of_comments', obj.comments.count())

class ThreadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('id', 'title', 'content', 'reading_date')
        read_only_fields = ('id',)

class CommentSerializer(serializers.ModelSerializer):
    thread = ThreadTitleSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'updated_at', 'thread')

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at')
        read_only_fields = ('id', 'created_at')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Book
        fields = (
            'id', 'title', 'description', 'customer_review_rank', 'author',
            'author_profile_img', 'author_info', 'author_works', 'cover_image',
            'audio_file', 'user', 'isbn', 'category'
        )
        read_only_fields = ('id', 'user')

class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'isbn', 'cover_image')

class RecommendedBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'description', 'category')
