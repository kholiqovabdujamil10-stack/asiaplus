from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),

    path('registration/', registration, name='registration'),
    path('confirm_email/', confirm_email, name='confirm_email'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),

    path('news/<int:pk>/', news_detail, name='news_detail'),
    path('category/<int:pk>/', category_news, name='category_news'),
    path('search/', search_news, name='search_news'),

    path('create_news/', create_news, name='create_news'),
    path('show_news/', show_news, name='show_news'),
    path('change_news/<int:pk>/', change_news, name='change_news'),
    path('delete_news/<int:pk>/', delete_news, name='delete_news'),

    path('create_comment/<int:pk>/', create_comment, name='create_comment'),
    path('my_comments/', my_comments, name='my_comments'),
    path('delete_comment/<int:pk>/', delete_comment, name='delete_comment'),
]
