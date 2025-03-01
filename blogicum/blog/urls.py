from django.urls import path

from . import views

app_name = "blog"
n = "category_posts"


urlpatterns = [
    path("", views.index, name="index"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path("posts/create/", views.add_post, name="create_post"),
    path("posts/<int:id>/edit/", views.edit_post, name="edit_post"),
    path("posts/<int:id>/delete/", views.delete_post, name="delete_post"),
    path("posts/<int:id>/comment/", views.add_comment, name="add_comment"),
    path(
        "posts/<int:id>/edit_comment/<int:comment_id>/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "posts/<int:id>/delete_comment/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),
    path("category/<slug:category_slug>/", views.category_posts, name=n),
    path("profile/<slug:name>/", views.profile, name="profile"),
    path(
        "profile/<slug:username>/edit/",
        views.edit_profile,
        name="edit_profile"
    ),
]
