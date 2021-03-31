from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа',
            slug='group'
        )
        cls.another_group = Group.objects.create(
            title='Групп',
            slug='s'
        )
        cls.user = User.objects.create_user(username='Amalia')
        Post.objects.create(
            text='aaaa',
            author=cls.user,
            group=cls.group,
        )
        cls.another_user = User.objects.create_user(username='a')
        cls.another_post = Post.objects.create(
            text='aa',
            author=cls.another_user,
            group=cls.another_group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': reverse('posts:group', kwargs={'slug': 'group'}),
            'posts/new_post.html': reverse('posts:new_post'),
            'profile.html': reverse(
                'posts:profile',
                kwargs={'username': 'Amalia'}
                            ),
            'post.html': reverse(
                'posts:post',
                kwargs={'username': 'Amalia', 'post_id': '1'}
                            ),
            'post_new.html': reverse('posts:post_edit', kwargs={'username': 'Amalia', 'post_id': '1'}),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name = reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_in_context = response.context['page'][0]
        self.assertEqual(post_in_context.text, 'aa')
        self.assertEqual(post_in_context.author, PostsViewsTests.another_user)
        self.assertEqual(post_in_context.group, PostsViewsTests.another_group)

    def test_new_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:group', kwargs={'slug': 'group'}))
        group = response.context['group']
        posts = response.context['page']
        self.assertEqual(group.title, PostsViewsTests.group.title)
        self.assertEqual(group.slug, PostsViewsTests.group.slug)
        self.assertNotIn(PostsViewsTests.another_group, posts)

    def test_profile_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Amalia'})
        )
        page = response.context['page']
        post = page[0]
        self.assertNotIn(PostsViewsTests.another_user, page)
        self.assertEqual(post.text, 'aaaa')
        self.assertEqual(post.group, PostsViewsTests.group)
        self.assertEqual(post.author, PostsViewsTests.user)

    def test_post_edit_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'username': 'Amalia', 'post_id': '1'}
                )
        )
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post',
                kwargs={'username': 'Amalia', 'post_id': '1'}
                )
        )
        post = response.context['post']
        num_posts = response.context['num_posts']
        self.assertEqual(post.text, 'aaaa')
        self.assertEqual(post.group, PostsViewsTests.group)
        self.assertEqual(post.author, PostsViewsTests.user)
        self.assertEqual(1, num_posts)


class PaginatorTestViews(TestCase):
    def setUp(self):
        self.group = Group.objects.create(
            title = 'Группа',
            slug = 'group'
        ) 
        self.user = User.objects.create_user(username='Amalia')
        for i in range(13):
            Post.objects.create(
                text=str(i),
                author=self.user,
                group=self.group,
            )
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

