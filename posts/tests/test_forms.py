from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()

class PostsFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Амалия')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'gagagaga'
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data = form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(
            Post.objects.filter(
               text='gagagaga',
               author=self.user
            ).exists()
        )

    def test_update_post(self):
        group = Group.objects.create(
            title='group',
            slug='group',
        )
        Post.objects.create(
            text='g',
            group=group,
            author=self.user
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'ga'
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': 'Амалия',
                    'post_id': '1'
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'Амалия'}
                )
            )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='ga',
                author=self.user,
                group=None,
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                text='g',
                group=group,
                author=self.user,
            ).exists()
        )
        
