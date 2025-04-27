from django.urls import path
from . import views

urlpatterns = [
    # 로그인
    path('login/', views.login_view, name='login'),

    # 로그아웃
    path('logout/', views.logout_view, name='logout'),

    # 회원가입
    path('signup/', views.signup, name='signup'),

    # 회원 정보 수정
    path('update/', views.update_profile, name='update_profile'),

    # 회원 삭제
    path('delete/', views.delete_profile, name='delete_profile'),

    # 비밀번호 변경
    path('change-password/', views.change_password, name='change_password'),

    # 프로필
    path('profile/', views.profile, name='profile'),

    # 팔로우
    path('follow/<int:user_id>/', views.follow, name='follow'),  # <int:user_id>는 팔로우할 사용자의 ID를 URL에서 받아옴
]
