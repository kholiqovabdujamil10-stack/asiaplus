from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class EmailConfirm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=150)
    caption = models.TextField()
    text = models.TextField()
    image = models.ImageField(upload_to='news/')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.TimeField(default=datetime.now)

    class Meta:
        permissions = [
            ('can_publish', 'User can publish news'),
            ('can_change', 'User can change news'),
            ('can_delete', 'User can delete news'),
            ('can_view', 'User can view news')
        ]

    def __str__(self):
        return self.title


class Comment(models.Model):
    name = models.CharField(max_length=100)
    caption = models.TextField()
    news_id = models.ForeignKey(News, on_delete=models.CASCADE)
    created_at = models.TimeField(default=datetime.now)
    def __str__(self):
        return self.name