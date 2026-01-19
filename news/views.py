"""Views for news app."""
from django.views.generic import ListView, DetailView, View
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from .models import Article, Comment
from .forms import CommentForm


class ArticleListView(ListView):
    """View for listing news articles."""

    model = Article
    template_name = "news/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(published=True).select_related("author")


class ArticleDetailView(DetailView):
    """View for article details."""

    model = Article
    template_name = "news/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return Article.objects.filter(published=True).select_related("author")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views += 1
        obj.save(update_fields=["views"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.get_approved_comments()
        context["form"] = CommentForm()
        return context


@method_decorator(login_required, name="dispatch")
class AddCommentView(View):
    """View for adding comments to articles."""

    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug, published=True)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Комментарий добавлен и ожидает модерации",
                    }
                )

            return redirect("article_detail", slug=slug)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": form.errors})

        return redirect("article_detail", slug=slug)


@method_decorator(login_required, name="dispatch")
class DeleteCommentView(View):
    """View for deleting comments (admin only)."""

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        # Check if user is admin or comment author
        if not (request.user.is_staff or request.user == comment.author):
            return JsonResponse({"success": False, "error": "Доступ запрещен"}, status=403)

        article_slug = comment.article.slug
        comment.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": True, "message": "Комментарий удален"}
            )

        return redirect("article_detail", slug=article_slug)


@method_decorator(login_required, name="dispatch")
class ApproveCommentView(View):
    """View for approving comments (admin only)."""

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        # Check if user is admin
        if not request.user.is_staff:
            return JsonResponse({"success": False, "error": "Доступ запрещен"}, status=403)

        comment.is_approved = not comment.is_approved
        comment.save(update_fields=["is_approved"])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            status = "одобрен" if comment.is_approved else "отклонен"
            return JsonResponse(
                {"success": True, "message": f"Комментарий {status}"}
            )

        return redirect("article_detail", slug=comment.article.slug)

