from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail
from random import randint
from .models import *


def registration(request):
    if request.method == 'POST':
        data = request.POST
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            is_active=False
        )

        code = str(randint(100000, 999999))
        EmailConfirm.objects.update_or_create(user=user, defaults={'code': code})

        send_mail('Confirm your email', f'Your confirmation code: {code}', None, [user.email])
        return redirect('confirm_email')

    return render(request, 'registration.html')


def confirm_email(request):
    if request.method == 'POST':
        user = User.objects.filter(username=request.POST.get('username')).first()

        if user:
            code_obj = EmailConfirm.objects.filter(user=user).first()

            if code_obj and code_obj.code == request.POST.get('code'):
                user.is_active = True
                user.save()
                code_obj.delete()
                user.groups.add(Group.objects.get(name='Users'))
                login(request, user)
                return redirect('profile')

        return redirect('confirm_email')

    return render(request, 'confirm_email.html')


def login_user(request):
    if request.method == 'POST':
        data = request.POST
        user = authenticate(request, username=data['username'], password=data['password'])

        if user is not None:
            login(request, user)
            return redirect('profile')

        return redirect('login')

    return render(request, 'login.html')


@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    return render(request, 'profile.html')


def home(request):
    news = News.objects.all().order_by('-id')
    categories = Category.objects.all()
    return render(request, 'home.html', {'news': news, 'categories': categories})


def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    comments = Comment.objects.filter(news_id=news)
    return render(request, 'detail.html', {'news': news, 'comments': comments})


def category_news(request, pk):
    category = get_object_or_404(Category, pk=pk)
    news = News.objects.filter(category_id=category)
    return render(request, 'home.html', {'news': news, 'categories': Category.objects.all()})


@login_required
def create_news(request):
    if not (request.user.groups.filter(name__in=['Editors', 'Admins']).exists() or request.user.is_superuser):
        return redirect('profile')

    if request.method == 'POST':
        data = request.POST
        News.objects.create(
            title=data['title'],
            caption=data['caption'],
            text=data['text'],
            image=request.FILES.get('image'),
            category_id_id=data['category'],
            user_id=request.user
        )
        return redirect('show_news')

    return render(request, 'create_news.html', {'categories': Category.objects.all()})


@login_required
def show_news(request):
    data = request.GET.get('query')

    if request.user.groups.filter(name='Editors').exists():
        news = News.objects.filter(user_id=request.user)
    elif request.user.groups.filter(name='Admins').exists() or request.user.is_superuser:
        news = News.objects.all()
    else:
        return redirect('profile')

    if data:
        news = news.filter(Q(title__icontains=data) | Q(caption__icontains=data))

    return render(request, 'show_news.html', {'news': news, 'data': data})


@login_required
def change_news(request, pk):
    news = get_object_or_404(News, pk=pk)
    is_admin = request.user.is_superuser or request.user.groups.filter(name='Admins').exists()
    is_editor = request.user.groups.filter(name='Editors').exists() and news.user_id == request.user

    if not (is_admin or is_editor):
        return redirect('profile')

    if request.method == 'POST':
        data = request.POST
        news.title = data['title']
        news.caption = data['caption']
        news.text = data['text']
        news.category_id_id = data['category']

        if request.FILES.get('image'):
            news.image = request.FILES.get('image')

        news.save()
        return redirect('news_detail', pk=pk)

    return render(request, 'change_news.html', {'news': news, 'categories': Category.objects.all()})


@login_required
def create_comment(request, pk):
    news = get_object_or_404(News, pk=pk)

    if request.method == 'POST':
        Comment.objects.create(
            name=request.user.username,
            caption=request.POST['caption'],
            news_id=news
        )

    return redirect('news_detail', pk=pk)


@login_required
def delete_news(request, pk):
    news = get_object_or_404(News, pk=pk)
    is_admin = request.user.is_superuser or request.user.groups.filter(name='Admins').exists()
    is_editor = request.user.groups.filter(name='Editors').exists() and news.user_id == request.user

    if not (is_admin or is_editor):
        return redirect('profile')

    if request.method == 'POST':
        news.delete()
        return redirect('show_news')

    return render(request, 'delete_news.html', {'news': news})


def search_news(request):
    data = request.GET.get('query')
    news = News.objects.all()

    if data:
        news = news.filter(Q(title__icontains=data) | Q(caption__icontains=data))

    return render(request, 'home.html', {
        'news': news,
        'categories': Category.objects.all(),
        'data': data
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        request.user.username = request.POST.get('username')
        request.user.email = request.POST.get('email')
        request.user.save()
        return redirect('profile')

    return render(request, 'edit_profile.html')


@login_required
def my_comments(request):
    comments = Comment.objects.filter(name=request.user.username)
    return render(request, 'my_comments.html', {'comments': comments})


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.name != request.user.username and not request.user.is_superuser:
        return redirect('profile')

    if request.method == 'POST':
        comment.delete()
        return redirect('my_comments')

    return render(request, 'delete_comment.html', {'comment': comment})