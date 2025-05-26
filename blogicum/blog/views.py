from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from . import models as m
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from .forms import CommentForm, PostForm, ProfileForm
from django.urls import reverse


def profile(request, name):
    profile = get_object_or_404(m.User, username=name)
    count = m.Comment.objects.filter(author=profile).count()
    publications = (
        m.Post.objects.select_related("author", "location", "category")
        .filter(author__username=name)
        .order_by("-pub_date")
    )
    paginator = Paginator(publications, 10)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)

    context = {"profile": profile, "page_obj": page_obj, "count": count}
    return render(request, "blog/profile.html", context)


@login_required
def add_comment(request, id):
    post = get_object_or_404(m.Post, pk=id)
    author = request.user
    form = CommentForm(request.POST)

    if form.is_valid():
        post.comment_count += 1
        post.save()
        comment = form.save(commit=False)
        comment.author = author
        comment.post = post
        comment.save()
        print(author, post)

        return redirect("blog:post_detail", id)

    return redirect("blog:post_detail", id)


@login_required
def edit_profile(request, username):
    user = get_object_or_404(m.User, username=username)
    if request.user == user:
        form = ProfileForm(request.POST or None, instance=user)
        context = {"form": form}
        if form.is_valid():
            form.save()

        return render(request, "blog/user.html", context)
    else:
        raise PermissionDenied


@login_required
def edit_comment(request, id, comment_id):
    comment = get_object_or_404(m.Comment, pk=comment_id)
    if request.user != comment.author:
        raise PermissionDenied

    form = CommentForm(
        request.POST or None, files=request.FILES or None, instance=comment
    )
    if form.is_valid():
        form.save()
        redirect_url = reverse("blog:post_detail", args=[id])

        return redirect(redirect_url)

    context = {"form": form, "comment": comment}

    return render(request, "blog/comment.html", context)


@login_required
def delete_comment(request, id, comment_id):
    comment = get_object_or_404(m.Comment, pk=comment_id)
    if request.user != comment.author:
        raise PermissionDenied

    post = get_object_or_404(m.Post, pk=id)
    if request.method == 'POST':
        post.comment_count -= 1
        post.save()
        comment.delete()
        return redirect('blog:post_detail', id)

    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def add_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    user = request.user

    if form.is_valid():
        post = form.save(commit=False)
        post.author = user
        post.save()
        redirect_url = reverse("blog:profile", args={post.author.username})
        return redirect(redirect_url)

    context = {"form": form}
    return render(request, "blog/create.html", context)


def edit_post(request, id):
    post = get_object_or_404(m.Post, pk=id)
    if not request.user.is_authenticated:
        return redirect('blog:post_detail', id)
    if request.user != post.author:
        return redirect('blog:post_detail', id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id)

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, id):
    post = get_object_or_404(m.Post, pk=id)
    if request.user != post.author:
        raise PermissionDenied

    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')

    context = {'post': post}
    return render(request, 'blog/create.html', context)


# class PostCreateView(CreateView):
#     form = PostForm
#     model = m.Post
#     template_name='blog/create.html'

# class PostDeleteView(DeleteView):
#     model = m.Post
#     template_name='blog/create.html'

# class CommentCreateView(CreateView):
#     form = CommentForm
#     model = m.Comment
#     template_name='blog/create.html'

# class CommentDeleteView(DeleteView):
#     model = m.Comment
#     template_name='blog/create.html'

# class CommentUpdateView(UpdateView):
#     form = CommentForm
#     model = m.Comment
#     template_name='blog/create.html'

# def comment_add(request, id):
#     form = CommentForm(request.POST or None)

#     if form.is_valid():
#         form.author = request.user.id
#         form.post = id
#         form.save()
#     return (request)


def index(request):
    paginator = Paginator(
        m.Post.objects.select_related("author", "location", "category")
        .order_by("-pub_date")
        .filter(
            Q(pub_date__lte=timezone.now())
            & Q(is_published=True)
            & Q(category__is_published=True)
        ),
        10,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    c = {"page_obj": page_obj}
    t = "blog/index.html"

    return render(request, t, c)


def category_posts(request, category_slug):
    category = get_object_or_404(m.Category, slug=category_slug)
    if category.is_published is False:
        raise Http404
    posts = (
        m.Post.objects.select_related("location")
        .filter(
            Q(category__slug=category_slug)
            & Q(is_published=True)
            & Q(pub_date__lte=timezone.now())
        )
        .order_by("-pub_date")
    )
    paginator = Paginator(posts, 10)
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)
    context = {
        "category": category,
        "page_obj": page_obj,
    }
    t = "blog/category.html"
    return render(request, t, context)


def post_detail(request, pk):
    post = get_object_or_404(m.Post, pk=pk)
    auth = "author"
    loc = "location"
    cat = "category"
    post = m.Post.objects.select_related(auth, loc, cat).get(pk=pk)

    if not post.is_published:
        if not request.user.is_authenticated or request.user != post.author:
            raise Http404
    elif post.pub_date > timezone.now() or post.category.is_published is False:
        raise Http404

    form = CommentForm(request.POST or None)
    comments = m.Comment.objects.filter(post=post.pk)
    context = {'post': post, 'form': form, 'comments': comments}
    template = 'blog/detail.html'

    return render(request, template, context)


# class PostDetailView(DetailView):
#     model = models.Post
#     template_name = 'blog/detail.html'

# class IndexTemplateView(TemplateView):
#     model = models.Post
#     template_name = 'blog/index.html'

# class CategoryListView(ListView):
#     model.
