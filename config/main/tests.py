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
        response = self.client.post(
            reverse('like_dislike'),
            data=json.dumps({'post_id': self.post.id, 'value': True}),
            content_type='application/json',
        )
        self.assertRedirects(response, reverse('login'))

    def test_existing_user_can_sign_in_and_remove_their_old_vote(self):
        LikeDislike.objects.create(user=self.user, post=self.post, value=True)
        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': 'StrongPass123',
        })
        self.assertRedirects(response, reverse('home'))

        response = self.client.post(
            reverse('like_dislike'),
            {'post_id': self.post.pk, 'value': True},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['user_reaction'])
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_json_like_can_be_changed_to_dislike_without_duplicate(self):
        self.client.login(username='tester', password='StrongPass123')
        url = reverse('like_dislike')

        like_response = self.client.post(
            url,
            data=json.dumps({'post_id': self.post.id, 'value': True}),
            content_type='application/json',
        )
        self.assertEqual(like_response.status_code, 200)
        self.assertEqual(like_response.json(), {
            'post_id': self.post.id,
            'likes': 1,
            'dislikes': 0,
            'user_reaction': True,
        })

        dislike_response = self.client.post(
            url,
            data=json.dumps({'post_id': self.post.id, 'value': False}),
            content_type='application/json',
        )
        self.assertEqual(dislike_response.status_code, 200)
        self.assertEqual(dislike_response.json(), {
            'post_id': self.post.id,
            'likes': 0,
            'dislikes': 1,
            'user_reaction': False,
        })
        self.assertEqual(LikeDislike.objects.filter(user=self.user, post=self.post).count(), 1)
        self.assertFalse(LikeDislike.objects.get(user=self.user, post=self.post).value)

        remove_response = self.client.post(
            url,
            data=json.dumps({'post_id': self.post.id, 'value': False}),
            content_type='application/json',
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertEqual(remove_response.json(), {
            'post_id': self.post.id,
            'likes': 0,
            'dislikes': 0,
            'user_reaction': None,
        })
        self.assertFalse(LikeDislike.objects.filter(user=self.user, post=self.post).exists())

    def test_invalid_json_reaction_is_rejected(self):
        self.client.login(username='tester', password='StrongPass123')
        response = self.client.post(
            reverse('like_dislike'),
            data=json.dumps({'post_id': self.post.id, 'value': 'not-a-boolean'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(LikeDislike.objects.filter(user=self.user, post=self.post).exists())

    def test_reaction_feed_returns_global_counts_and_viewer_reaction(self):
        other_user = User.objects.create_user(username='other', password='StrongPass123')
        LikeDislike.objects.create(user=self.user, post=self.post, value=True)
        LikeDislike.objects.create(user=other_user, post=self.post, value=False)
        url = reverse('post_reactions')

        self.client.login(username='tester', password='StrongPass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn({
            'id': self.post.id,
            'likes_count': 1,
            'dislikes_count': 1,
            'user_reaction': True,
        }, response.json()['posts'])

        self.client.logout()
        response = self.client.get(url)
        self.assertIn({
            'id': self.post.id,
            'likes_count': 1,
            'dislikes_count': 1,
            'user_reaction': None,
        }, response.json()['posts'])


class GameReactionTests(TestCase):
    def test_catalog_shows_counts_for_the_same_post_as_the_reaction_feed(self):
        post = Post.objects.get(catalog_key='space-battle')
        post.title = 'Renamed Space Battle post'
        post.save(update_fields=['title'])
        Post.objects.create(title='Space Battle', content='Unlinked duplicate')
        user = User.objects.create_user(username='catalog_voter')
        LikeDislike.objects.create(user=user, post=post, value=True)

        catalog = self.client.get(reverse('games'))
        self.assertContains(catalog, f'data-post-id="{post.pk}"')
        self.assertContains(catalog, '<td class="likes-count">1</td>', html=True)
        self.assertContains(catalog, reverse('post_reactions'))

        feed = self.client.get(reverse('post_reactions')).json()['posts']
        self.assertIn({
            'id': post.pk,
            'likes_count': 1,
            'dislikes_count': 0,
            'user_reaction': None,
        }, feed)


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
        self.assertIn({
            'id': post.id,
            'likes_count': 1,
            'dislikes_count': 0,
            'user_reaction': None,
        }, response.json()['posts'])
