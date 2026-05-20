from django.conf import settings
from django.db import models


class Feedback(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.created_at:%d.%m.%Y %H:%M}"


# Дополнительная модель к стандартному пользователю Django.
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title


# Одна реакция от одного пользователя к одному посту.
class LikeDislike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.BooleanField()  # True = like, False = dislike

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        action = 'Лайк' if self.value else 'Дизлайк'
        return f"{self.user} - {self.post} - {action}"
