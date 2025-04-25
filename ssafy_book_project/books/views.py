from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Thread
from accounts.models import User
from .forms import ThreadForm, BookForm
from .utils import (
    process_wikipedia_info,
    generate_author_gpt_info,
    generate_audio_script,
    create_tts_audio,
)


def index(request):
    books = Book.objects.all()
    context = {
        "books": books,
    }
    return render(request, "books/index.html", context)

@login_required
def create(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)

            wiki_summary = process_wikipedia_info(book)
            author_info, author_works = generate_author_gpt_info(book, wiki_summary)
            book.author_info = author_info
            book.author_works = author_works
            book.user = request.user
            book.save()

            audio_script = generate_audio_script(book, wiki_summary)
            audio_file_path = create_tts_audio(book, audio_script)
            if audio_file_path:
                book.audio_file = audio_file_path
                book.save()

            return redirect("books:detail", book.pk)
    else:
        form = BookForm()
    context = {"form": form}
    return render(request, "books/create.html", context)

def detail(request, pk):
    book = Book.objects.get(pk=pk)
    threads = Thread.objects.filter(book_id=book)  # 인스턴스로 필터링
    if request.method == "POST":
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.book_id = book           # 인스턴스 할당!
            thread.user_id = request.user.id  # 숫자(ID) 할당!
            thread.save()
            return redirect("books:detail", pk=book.id)
    else:
        form = ThreadForm()
    context = {
        "book": book,
        "threads": threads,
        "form": form,
    }
    return render(request, "books/detail.html", context)

@login_required
def update(request, pk):
    book = Book.objects.get(pk=pk)
    if request.user != book.user:  # user_id → user로 수정
        return redirect('books:detail', pk)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect("books:detail", pk)
    else:
        form = BookForm(instance=book)
    context = {
        "form": form,
        "book": book,
    }
    return render(request, "books/update.html", context)

@login_required
def delete(request, pk):
    book = Book.objects.get(pk=pk)
    if request.user == book.user:  # user_id → user로 수정
        book.delete()
    return redirect("books:index")

@login_required
def thread_create(request, pk):
    if request.method == "POST":
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.book_id = Book.objects.get(pk=pk)  # 인스턴스 할당!
            thread.user_id = request.user.id        # 숫자(ID) 할당!
            thread.save()
            return redirect("books:detail", pk)
    else:
        form = ThreadForm()
    context = {"form": form}
    return render(request, "threads/create.html", context)

def thread_detail(request, pk, thread_pk):
    book = Book.objects.get(pk=pk)
    thread = Thread.objects.get(pk=thread_pk)
    is_liked = False
    if request.user.is_authenticated:
        is_liked = thread.likes.filter(id=request.user.id).exists()
    context = {
        'thread': thread,
        'book': book,
        'is_liked': is_liked,
        'total_likes': thread.likes.count(),
        'user': request.user,
    }
    return render(request, "threads/detail.html", context)
    

@login_required
def thread_update(request, pk, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    book = Book.objects.get(pk=pk)  # book 객체 가져오기

    if request.user != thread.user:
        return redirect('books:thread_detail', pk, thread_pk)
    if request.method == "POST":
        form = ThreadForm(request.POST, request.FILES, instance=thread)
        if form.is_valid():
            form.save()
            return redirect("books:thread_detail", pk, thread_pk)
    else:
        form = ThreadForm(instance=thread)
    context = {
        "form": form,
        "thread": thread,
        "book": book,  # 반드시 추가!
    }
    return render(request, "threads/update.html", context)


@login_required
def thread_delete(request, pk, thread_pk):  # pk 매개변수 추가
    thread = get_object_or_404(Thread, pk=thread_pk)
    if request.user == thread.user:
        thread.delete()
    return redirect('books:detail', pk=pk)  # Thread가 아닌 Book 상세 페이지로 리디렉션



@login_required
def thread_like(request, pk, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    if thread.likes.filter(id=request.user.id).exists():
        thread.likes.remove(request.user)
    else:
        thread.likes.add(request.user)
    return redirect('books:thread_detail', pk=pk, thread_pk=thread_pk)
