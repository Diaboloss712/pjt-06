from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Thread, Category, Comment
from accounts.models import User
from .serializers import ThreadListSerializer, ThreadSerializer, CommentSerializer, BookSerializer, CategorySerializer
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .forms import ThreadForm, BookForm
from .utils import (
    process_wikipedia_info,
    generate_author_gpt_info,
    generate_audio_script,
    create_tts_audio,
)

@api_view(['GET'])
def index(request):
    books = Book.objects.all()
    context = {
        "books": books,
    }
    return render(request, "books/index.html", context)

@api_view(['POST'])
@login_required
def create(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()

            serializer = BookSerializer(book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
          
    else:
        form = BookForm()
    context = {"form": form}
    return render(request, "books/create.html", context)

@api_view(['GET','POST'])
def detail(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    threads = Thread.objects.filter(book_id=book)

    if request.method == "POST":
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.book_id = book         
            thread.user_id = request.user.id  
            thread.save()
            return redirect("books:detail", pk=book.id)
    else:
        form = ThreadForm()
    
    book_serializer = BookSerializer(book)
    thread_serializer = ThreadListSerializer(threads, many=True)

    context = {
        "book": book_serializer.data,
        "threads": thread_serializer.data,
        "form": form,
    }
    return render(request, "books/detail.html", context)

@api_view(['POST'])
@login_required
def update(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    if request.user != book.user:  # user_id → user로 수정
        return redirect('books:detail', book_pk)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect("books:detail", book_pk)
    else:
        form = BookForm(instance=book)
    context = {
        "form": form,
        "book": book,
    }
    return render(request, "books/update.html", context)

@api_view(['DELETE'])
@login_required
def delete(request, book_pk):
    book = Book.objects.get(pk=book_pk)
    if request.user == book.user:  
        book.delete()
    return redirect("books:index")

# 전체 쓰레드 목록
@api_view(['GET'])
def thread_list(request):
    threads = Thread.objects.all()
    serializer = ThreadListSerializer(threads, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@login_required
@api_view(['POST'])
def create_thread(request, book_pk):
    serializer = ThreadSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        book = get_object_or_404(Book, pk=book_pk)
        user = request.user.id
        serializer.save(book=book, user=user)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def thread_detail(request, book_pk, thread_pk):
    book = Book.objects.get(pk=book_pk)
    thread = get_object_or_404(Thread, pk=thread_pk)
    thread = Thread.objects.annotate(num_of_comments=Count('comment')).get(pk=thread.pk)
    serializer = ThreadSerializer(thread)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@login_required
def thread_update(request, book_pk, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.user != thread.user:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = ThreadSerializer(instance = thread, data=request.data, partial = True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['DELETE'])
def thread_delete(request, book_pk, thread_pk):  
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.user == thread.user:
        thread.delete()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@login_required
def create_comment(request, book_pk, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(thread_id = thread)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def comment_detail(request, book_pk, thread_pk, comment_pk):
    book = Book.objects.get(pk=book_pk)
    thread = Thread.objects.get(pk=thread_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    serializer = ThreadSerializer(thread)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@login_required
def update_comment(request, book_pk, thread_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user != comment.user:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = CommentSerializer(instance = comment, data=request.data, partial = True)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['DELETE'])
def delete_comment(request, book_pk, thread_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user:
        comment.delete()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['POST'])
def thread_like(request, book_pk, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    if thread.likes.filter(id=request.user.id).exists():
        thread.likes.remove(request.user)
    else:
        thread.likes.add(request.user)
    return Response(status=status.HTTP_200_OK)

#전체 카테고리 목록 제공
@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()  
    serializer = CategorySerializer(categories, many=True)  
    return Response(serializer.data, status=status.HTTP_200_OK) 

#전체 도서 목록 제공
@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()  
    serializer = BookSerializer(books, many=True)  
    return Response(serializer.data, status=status.HTTP_200_OK)  
