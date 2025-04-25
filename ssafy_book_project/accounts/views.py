from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import UserUpdateForm, UserLoginForm, UserForm
from .models import User
from books.models import Thread  # Thread 모델 임포트

# 로그인
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

# 로그아웃
def logout_view(request):
    logout(request)
    return redirect('login')

# 회원가입
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserForm()
    return render(request, 'accounts/signup.html', {'form': form})

# 회원 정보 수정
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/update.html', {'form': form})

# 회원 삭제
@login_required
def delete_profile(request):
    request.user.delete()
    return redirect('index')

# 비밀번호 변경
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('index')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

# 프로필 (자신/타인 모두 지원)
@login_required
def profile(request, username=None):
    if username is None or username == request.user.username:
        user_profile = request.user
        is_own_profile = True
    else:
        user_profile = get_object_or_404(User, username=username)
        is_own_profile = False

    threads = Thread.objects.filter(user=user_profile).order_by('-created_at')
    is_following = False
    if request.user.is_authenticated and not is_own_profile:
        is_following = request.user.followers.filter(id=user_profile.id).exists()

    context = {
        'user_profile': user_profile,
        'threads': threads,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'follower_count': user_profile.followers.count(),
        'following_count': user_profile.following.count(),
    }
    return render(request, 'accounts/profile.html', context)

# 팔로우/언팔로우
@login_required
def follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if request.user.id == user_id:
        return redirect('profile')
    if request.user.followers.filter(id=user_id).exists():
        request.user.followers.remove(user_to_follow)
    else:
        request.user.followers.add(user_to_follow)
    return redirect('profile', username=user_to_follow.username)

# 팔로워 목록
@login_required
def followers(request, username=None):
    if username is None:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    followers_list = user.followers.all()
    return render(request, 'accounts/followers.html', {'followers': followers_list, 'user_profile': user})

# 팔로잉 목록
@login_required
def following(request, username=None):
    if username is None:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    following_list = user.following.all()
    return render(request, 'accounts/following.html', {'following': following_list, 'user_profile': user})

def index(request):
    return render(request, 'accounts/index.html')
