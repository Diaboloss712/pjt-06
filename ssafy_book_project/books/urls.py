from django.urls import path
from . import views


app_name = "books"
urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("<int:book_pk>/", views.detail, name="detail"),
    path("<int:book_pk>/update/", views.update, name="update"),
    path("<int:book_pk>/delete/", views.delete, name="delete"),
    path("<int:book_pk>/threads/", views.thread_list, name='thread_list'),
    path("<int:book_pk>/threads/create/", views.create_thread, name='create_thread'),
    path("<int:book_pk>/threads/<int:thread_pk>/", views.thread_detail, name='thread_detail'),
    path("<int:book_pk>/threads/<int:thread_pk>/update/", views.thread_update, name='thread_update'),
    path("<int:book_pk>/threads/<int:thread_pk>/delete/", views.thread_delete, name='thread_delete'),
    # path("<int:book_pk>/threads/<int:thread_pk>/like/", views.thread_like, name='thread_like'),
    path("<int:book_pk>/threads/<int:thread_pk>/comments/create", views.create_comment, name='create_comment'),
    path("<int:book_pk>/threads/<int:thread_pk>/comments/<int:comment_pk>", views.comment_detail, name='comment_detail'),
    path("<int:book_pk>/threads/<int:thread_pk>/comments/<int:comment_pk>/update", views.update_comment, name='update_comment'),
    path("<int:book_pk>/threads/<int:thread_pk>/comments/<int:comment_pk>/delete", views.delete_comment, name='delete_comment'),

    path('categories/', views.category_list, name='category_list'), 
    path('books/', views.book_list, name='book_list'),  

    path("<int:book_pk>/recommendations/", views.recommend_book_list, name="recommend"),
]
