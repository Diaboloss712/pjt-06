from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Thread, Category, Comment
from accounts.models import User
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, permissions
from .utils import (
    process_wikipedia_info,
    generate_author_gpt_info,
    generate_audio_script,
    create_tts_audio,
    get_embedding,
    recommend_books,
)

from drf_spectacular.utils import extend_schema
from .serializers import(
    ThreadListSerializer,
    ThreadSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    BookSerializer,
    CategorySerializer,
    BookListSerializer,
    ThreadCreateSerializer,
    RecommendedBookSerializer,
)

@extend_schema(summary="책 목록 조회", responses=BookListSerializer)
@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
    books = Book.objects.all()
    serializer = BookListSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(summary="책 생성", request=BookSerializer, responses=BookSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        book = serializer.save(user=request.user)
        
        wiki_summary = process_wikipedia_info(book)
        author_info, author_works = generate_author_gpt_info(book, wiki_summary)
        book.author_info = author_info
        book.author_works = author_works
        book.save()

        audio_script = generate_audio_script(book, wiki_summary)
        audio_file_path = create_tts_audio(book, audio_script)
        if audio_file_path:
            book.audio_file = audio_file_path
            book.save()

        return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)

@extend_schema(summary="책 상세 조회", responses=BookSerializer)
@api_view(['GET'])
@permission_classes([AllowAny])
def detail(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    serializer = BookSerializer(book)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(summary="책 수정", request=BookSerializer, responses=BookSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    if request.user != book.user:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = BookSerializer(instance=book, data=request.data, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(summary="책 삭제", responses={200:None})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    if request.user == book.user:
        book.delete()
    return Response(status=status.HTTP_200_OK)

@extend_schema(summary="전체 쓰레드 조회", responses=ThreadListSerializer(many=True))
@api_view(['GET'])
def thread_list(request):
    threads = Thread.objects.all()
    serializer = ThreadListSerializer(threads, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(summary="쓰레드 생성", request=ThreadCreateSerializer, responses=ThreadSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_thread(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    serializer = ThreadCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(book=book, user=request.user)
        return Response(ThreadSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)

@extend_schema(summary="쓰레드 상세 조회", responses=ThreadSerializer)
@api_view(['GET'])
def thread_detail(request, book_pk, thread_pk):
    thread = Thread.objects.annotate(num_of_comments=Count('comments')).get(pk=thread_pk)
    serializer = ThreadSerializer(thread)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(summary="쓰레드 수정", request=ThreadSerializer, responses=ThreadSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def thread_update(request, book_pk, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.user != thread.user:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = ThreadCreateSerializer(instance=thread, data=request.data, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(ThreadSerializer(serializer.instance).data, status=status.HTTP_200_OK)

@extend_schema(summary="쓰레드 삭제", responses={200:None})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def thread_delete(request, book_pk, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.user == thread.user:
        thread.delete()
    return Response(status=status.HTTP_200_OK)

@extend_schema(summary="댓글 생성", request=CommentCreateSerializer, responses=CommentSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, book_pk, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    serializer = CommentCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(thread=thread, user=request.user)
        return Response(CommentSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)

@extend_schema(summary="댓글 상세 조회", responses=CommentSerializer)
@api_view(['GET'])
def comment_detail(request, book_pk, thread_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(summary="댓글 수정", request=CommentSerializer, responses=CommentSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_comment(request, book_pk, thread_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user != comment.user:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = CommentCreateSerializer(instance=comment, data=request.data, partial=True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(CommentSerializer(serializer.instance).data, status=status.HTTP_200_OK)

@extend_schema(summary="댓글 삭제", responses={200:None})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, book_pk, thread_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user:
        comment.delete()
    return Response(status=status.HTTP_200_OK)

# @extend_schema(summary="쓰레드 좋아요/좋아요 취소")
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def thread_like(request, book_pk, thread_pk):
#     thread = get_object_or_404(Thread, pk=thread_pk)
#     if thread.likes.filter(id=request.user.id).exists():
#         thread.likes.remove(request.user)
#     else:
#         thread.likes.add(request.user)
#     return Response(status=status.HTTP_200_OK)

@extend_schema(summary="카테고리 전체 조회", responses=CategorySerializer(many=True))
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(summary="도서 전체 조회", responses=BookSerializer(many=True))
@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def recommend_book_list(request, book_pk):
    try:
        target_book = Book.objects.get(pk=book_pk)
    except Book.DoesNotExist:
        return Response({"detail": "해당 책을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    category_books = list(Book.objects.filter(category=target_book.category))
    category_count = len(category_books) - 1

    recommended = recommend_books(
        target_book=target_book,
        all_books=category_books,
        embedding_fn=get_embedding,
        top_k=5
    )
    recommended_books = [book for book, _ in recommended]
    serializer = RecommendedBookSerializer(recommended_books, many=True)
    return Response({
        "message": f"같은 카테고리 내 {category_count}권 중 {len(recommended_books)}권을 추천합니다.",
        "recommendations": serializer.data,
    })