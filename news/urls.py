"""URL patterns for news app."""
from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    AddCommentView,
    DeleteCommentView,
    ApproveCommentView,
)

urlpatterns = [
    path("", ArticleListView.as_view(), name="article_list"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article_detail"),
    path("<slug:slug>/comment/add/", AddCommentView.as_view(), name="add_comment"),
    path("comment/<int:pk>/delete/", DeleteCommentView.as_view(), name="delete_comment"),
    path("comment/<int:pk>/approve/", ApproveCommentView.as_view(), name="approve_comment"),
]
