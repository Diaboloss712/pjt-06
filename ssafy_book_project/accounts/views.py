from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import (
    UserSerializer,
    UserSignupSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserLoginSerializer,
)
from books.models import Thread

# 로그인
@extend_schema(request=UserLoginSerializer, responses=UserSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 로그아웃
@extend_schema(responses={204: None})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)

# 회원가입
@extend_schema(request=UserSignupSerializer, responses=UserSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 회원 정보 수정
@extend_schema(request=UserUpdateSerializer, responses=UserSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 회원 삭제
@extend_schema(responses={204: None})
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile(request):
    request.user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# 비밀번호 변경
@extend_schema(request=ChangePasswordSerializer, responses={204: None})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        update_session_auth_hash(request, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 프로필 조회
@extend_schema(responses=UserSerializer)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request, username=None):
    if username is None or username == request.user.username:
        user_profile = request.user
    else:
        user_profile = get_object_or_404(User, username=username)

    serializer = UserSerializer(user_profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 팔로우/언팔로우
@extend_schema(responses={204: None})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if request.user.id == user_id:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if request.user.followers.filter(id=user_id).exists():
        request.user.followers.remove(user_to_follow)
    else:
        request.user.followers.add(user_to_follow)
    return Response(status=status.HTTP_204_NO_CONTENT)

# 팔로워 목록
@extend_schema(responses=UserSerializer(many=True))
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def followers(request, username=None):
    if username is None:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    followers_list = user.followers.all()
    serializer = UserSerializer(followers_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# 팔로잉 목록
@extend_schema(responses=UserSerializer(many=True))
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def following(request, username=None):
    if username is None:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    following_list = user.following.all()
    serializer = UserSerializer(following_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
