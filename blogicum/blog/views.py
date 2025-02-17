from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from . import models as m
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.generic import CreateView, DeleteView, UpdateView
from .forms import CommentForm, PostForm
from django.contrib.auth.forms import UserCreationForm

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

def forbidden(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)

def server_error(request):
    return render(request, 'pages/500.html', status=500)


def profile(request, name):
    profile = m.User.objects.get(username=name)
    publications = m.Post.objects.select_related("author", "location", "category").filter(author__username=name)
    paginator = Paginator(publications, 10)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    context = {
        'profile' : profile,
        'page_obj' : page_obj
    }
    return render(request, 'blog/profile.html', context)

@login_required
def add_comment(request, id):
    post = get_object_or_404(m.Post, pk=id)
    author = request.user
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = author
        comment.post = post
        comment.save()
        print(author, post)
        return redirect('blog:post_detail', id)
    
    
    return redirect('blog:post_detail', id)

@login_required
def edit_profile(request, username):
    user = get_object_or_404(m.User, username=username)
    if request.user == user:
        form = UserCreationForm(request.POST or None, instance=user)
        context = {'form' : form}
        return render(request, 'blog/user.html', context)
    
    return Http404()

    

@login_required
def edit_comment(request, id, comment_id):
    comment = get_object_or_404(m.Comment, pk=comment_id)
    form = CommentForm(
        request.POST or None,
        files=request.FILES or None,
        instance=comment
    )
    if form.is_valid():
        form.save()

        return redirect('blog:post_detail', id)

    context = {'form' : form} 

    return render(request, 'blog/comment.html', context)

@login_required
def delete_comment(request, id, comment_id):
    comment = get_object_or_404(m.Comment, pk=comment_id)
    form = CommentForm(
        instance=comment
    )

    if request.POST:
        form.instance.delete()

        return redirect('blog:post_detail', id)

    context = {'form' : form} 


    return render(request, 'blog/comment.html', context)

@login_required
def add_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    user = m.User(request.user)


    if form.is_valid():
        form.save(commit=False)
        form.author = user
        form.save()

    context = {'form' : form}
    return render(request, 'blog/create.html', context)

@login_required
def edit_post(request, id):
    post = get_object_or_404(m.Post, pk=id)

    form = PostForm(
        request.POST or None,
        instance=post
    )


    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id)

    context = {'form' : form}

    return render(request, 'blog/create.html', context)

@login_required
def delete_post(request, id):
    post = get_object_or_404(m.Post, pk=id)

    form = PostForm(
        instance=post
    )

    context={'form' : form}

    if request.POST:
        post.delete()


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
    paginator = Paginator(m.Post.objects.select_related("author", "location", "category")
        .order_by("pub_date")
        .filter(
            Q(pub_date__lte=timezone.now())
            & Q(is_published=True)
            & Q(category__is_published=True)
        ), 10)
    
    page_number = request.GET.get('page')
    # Получаем запрошенную страницу пагинатора. 
    # Если параметра page нет в запросе или его значение не приводится к числу,
    # вернётся первая страница.
    page_obj = paginator.get_page(page_number)
    c = {"page_obj": page_obj}
    t = "blog/index.html"
    
    return render(request, t, c)



def category_posts(request, category_slug):
    category = get_object_or_404(m.Category, slug=category_slug)
    if category.is_published is False:
        raise Http404
    posts = m.Post.objects.select_related("location").filter(
            Q(category__slug=category_slug)
            & Q(is_published=True)
            & Q(pub_date__lte=timezone.now())
        )
    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    context = {
        "category": category,
        "page_obj": page_obj
    }
    t = "blog/category.html"
    return render(request, t, context)


def post_detail(request, pk):
    post = get_object_or_404(m.Post, pk=pk)
    auth = "author"
    loc = "location"
    cat = "category"
    post = m.Post.objects
    post = post.select_related(auth, loc, cat).get(pk=pk)
    if (
        post.pub_date > timezone.now()
        or post.is_published is False
        or post.category.is_published is False
    ):
        raise Http404
    
    form = CommentForm(request.POST or None)

    # if form.is_valid():
    #     form.save(commit=False)
    #     form.post = post
    #     form.author = request.user
    #     form.save()
    comments = m.Comment.objects.filter(post=post.pk)
    context = {"post": post, 'form' : form, 'comments' : comments}
    template = "blog/detail.html"

    return render(request, template, context)


# class PostDetailView(DetailView):
#     model = models.Post
#     template_name = 'blog/detail.html'

# class IndexTemplateView(TemplateView):
#     model = models.Post
#     template_name = 'blog/index.html'

# class CategoryListView(ListView):
#     model.
