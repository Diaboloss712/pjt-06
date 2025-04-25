from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),  # 관리자 페이지 URL
    path("books/", include("books.urls")),  # books 앱의 URL 포함
    path("accounts/", include("accounts.urls")),  # accounts 앱의 URL 포함
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 미디어 파일 제공
