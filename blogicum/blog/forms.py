from django.forms import ModelForm
from .models import Comment, Post, User


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ("text",)


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = "__all__"
        exclude = ("author", "comment_count")


class ProfileForm(ModelForm):

    class Meta:
        model = User
        fields = ("username", "last_name", "first_name", "email")
