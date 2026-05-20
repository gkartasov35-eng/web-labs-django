import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import LikeDislike, Post, UserProfile

User = get_user_model()


class RegistrationTests(TestCase):
    def test_user_is_created_from_registration_form(self):
        response = self.client.post(reverse('auth'), {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'ivanov',
            'email': 'ivan@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='ivanov').exists())

    def test_password_is_hashed(self):
        self.client.post(reverse('auth'), {
            'first_name': 'Петр',
            'last_name': 'Петров',
            'username': 'petrov',
            'email': 'petrov@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        user = User.objects.get(username='petrov')

        self.assertNotEqual(user.password, 'StrongPass123')
        self.assertTrue(user.check_password('StrongPass123'))
        self.assertIn('pbkdf2_', user.password)

    def test_profile_is_created(self):
        self.client.post(reverse('auth'), {
            'first_name': 'Анна',
            'last_name': 'Сидорова',
            'username': 'anna',
            'email': 'anna@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        user = User.objects.get(username='anna')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(username='olduser', email='same@example.com', password='StrongPass123')
        response = self.client.post(reverse('auth'), {
            'first_name': 'Олег',
            'last_name': 'Смирнов',
            'username': 'newuser',
            'email': 'same@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertContains(response, 'Пользователь с таким email уже существует.')
        self.assertFalse(User.objects.filter(username='newuser').exists())


class LikeDislikeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='StrongPass123')
        self.post = Post.objects.create(title='Тестовый пост', content='Содержимое')

    def test_like_dislike_requires_auth(self):
        response = self.client.post(reverse('like_dislike'), {
            'post_id': self.post.id,
            'value': 'true',
        })
        self.assertEqual(response.status_code, 302)

    def test_like_is_saved_for_authorized_user(self):
        self.client.login(username='tester', password='StrongPass123')
        response = self.client.post(reverse('like_dislike'), {
            'post_id': self.post.id,
            'value': 'true',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(LikeDislike.objects.filter(user=self.user, post=self.post, value=True).exists())


class AjaxJsonTests(TestCase):
    def test_feedback_accepts_json(self):
        response = self.client.post(
            reverse('feedback'),
            data=json.dumps({
                'name': 'Иван',
                'email': 'ivan@example.com',
                'message': 'Тестовое сообщение',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': 'Сообщение отправлено!'})

    def test_reaction_counters_are_returned_as_json(self):
        user = User.objects.create_user(username='ajax_user', password='StrongPass123')
        post = Post.objects.create(title='JSON пост', content='Содержимое')
        LikeDislike.objects.create(user=user, post=post, value=True)

        response = self.client.get(reverse('post_reactions'))

        self.assertEqual(response.status_code, 200)
        self.assertIn({'id': post.id, 'likes_count': 1, 'dislikes_count': 0}, response.json()['posts'])
