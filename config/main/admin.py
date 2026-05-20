from django.contrib import admin
from .models import Feedback, UserProfile, Post, LikeDislike


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'message')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title', 'content')


@admin.register(LikeDislike)
class LikeDislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'value')
    list_filter = ('value',)
    search_fields = ('user__username', 'post__title')
