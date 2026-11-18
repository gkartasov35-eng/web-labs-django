from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import auth_view

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('games/', views.games, name='games'),
    path('auth/', auth_view, name='auth'),
    path('login/', LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('feedback/', views.feedback, name='feedback'),
    path('like_dislike/', views.like_dislike, name='like_dislike'),
    path('post_reactions/', views.post_reactions, name='post_reactions'),
]
