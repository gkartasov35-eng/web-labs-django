import json
import os

import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import RegisterForm
from .models import Feedback, LikeDislike, Post, UserProfile

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL', '')


def send_telegram_message(text):
    """Отправка вынесена отдельно: в Docker она может идти через микросервис уведомлений."""
    if NOTIFICATION_SERVICE_URL:
        try:
            response = requests.post(
                f"{NOTIFICATION_SERVICE_URL.rstrip('/')}/send/",
                json={"text": text},
                timeout=5,
            )
            return response.ok
        except requests.RequestException:
            return False

    if not TOKEN or not CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=data, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return False
    return True


def get_posts_with_reactions():
    # Счётчики сразу подтягиваются из БД, чтобы при загрузке страницы не было нулей.
    return Post.objects.annotate(
        likes_count=Count('likedislike', filter=Q(likedislike__value=True)),
        dislikes_count=Count('likedislike', filter=Q(likedislike__value=False)),
    )


def home(request):
    posts = get_posts_with_reactions()
    return render(request, 'home.html', {'posts': posts})


def about(request):
    return render(request, 'about.html')


def games(request):
    return render(request, 'games.html')


def auth_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(
                request,
                'Регистрация прошла успешно. Пользователь создан, пароль сохранён в зашифрованном виде.'
            )
            return redirect('home')
        messages.error(request, 'Исправьте ошибки в форме регистрации.')
    else:
        form = RegisterForm()

    return render(request, 'main/auth.html', {'form': form})


@require_http_methods(["GET", "POST"])
def feedback(request):
    if request.method == "POST":
        try:
            if request.headers.get('Content-Type', '').startswith('application/json'):
                data = json.loads(request.body.decode('utf-8') or '{}')
            else:
                data = request.POST
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Некорректный JSON."}, status=400)

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        message = str(data.get("message", "")).strip()

        if name and message:
            Feedback.objects.create(name=name, message=message)
            text = f"Новое сообщение!\nИмя: {name}\nEmail: {email}\nСообщение: {message}"
            send_telegram_message(text)

            # Для 6-й лабы возвращаем JSON, чтобы страница обновлялась без перезагрузки.
            return JsonResponse({"success": True, "message": "Сообщение отправлено!"})

        return JsonResponse({"success": False, "message": "Заполните все поля."}, status=400)

    return render(request, "main/feedback.html")


@login_required
@require_POST
def like_dislike(request):
    post_id = request.POST.get("post_id")
    value_raw = request.POST.get("value")

    if post_id is None or value_raw is None:
        return JsonResponse({"error": "Не переданы обязательные данные"}, status=400)

    post = get_object_or_404(Post, id=post_id)
    value = value_raw.lower() == "true"

    LikeDislike.objects.update_or_create(
        user=request.user,
        post=post,
        defaults={"value": value}
    )

    likes = LikeDislike.objects.filter(post=post, value=True).count()
    dislikes = LikeDislike.objects.filter(post=post, value=False).count()

    return JsonResponse({"post_id": post.id, "likes": likes, "dislikes": dislikes})


def post_reactions(request):
    posts = get_posts_with_reactions().values('id', 'likes_count', 'dislikes_count')
    return JsonResponse({"posts": list(posts)})
