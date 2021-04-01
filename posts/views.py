from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def index(request):
    paginator = Paginator(Post.objects.all(), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    paginator = Paginator(group.posts.all(), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


class NewPostView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    success_url = reverse_lazy('posts:index')
    template_name = 'posts/new_post.html'

    def form_valid(self, form):
        new_post = form.save(commit=False)
        new_post.author = self.request.user
        new_post.save()
        return super().form_valid(form)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    paginator = Paginator(author.posts.all(), 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    num_posts = author.posts.count()
    context = {
        'num_posts': num_posts,
        'page': page,
        'author': author
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    num_posts = author.posts.count()
    context = {
        'author': author,
        'post': post,
        'num_posts': num_posts
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        author__username=username)
    if request.user.username == username:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect(
                    reverse_lazy(
                        'posts:post',
                        kwargs={'username': username, 'post_id': post_id}
                    )
                )
            return render(request, 'post_new.html', {'form': form})
        form = PostForm(
            initial={
                'text': post.text,
                'group': post.group},)
        context = {
            'form': form
        }
        return render(request, 'post_new.html', context)
    return redirect(
        reverse_lazy(
            'posts:profile',
            kwargs={'username': username}
        )
    )
