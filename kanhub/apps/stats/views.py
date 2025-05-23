__all__ = ()
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.repositories.models import Commit, Repository, Task


class RepositoryStatistics(TemplateView):
    template_name = "stats/repository_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        repository = get_object_or_404(Repository, pk=self.kwargs["pk"])

        if (
            not repository.is_published
            and self.request.user not in repository.users.all()
        ):
            raise Http404("Репозиторий недоступен.")

        commits = Commit.objects.filter(
            repository=repository,
        ).all()

        commit = commits.last()
        tasks = Task.objects.filter(
            commit=commit,
        ).all()

        commits_count = repository.commit_set.count()
        tasks_count = tasks.count()
        latest_commit = repository.commit_set.order_by("-created_at").first()

        tasks_by_tags = (
            tasks.filter(commit__repository=repository)
            .values("tags__name")
            .annotate(count=Count("tags"))
        )

        context.update(
            {
                "repository": repository,
                "commits_count": commits_count,
                "tasks_count": tasks_count,
                "latest_commit": latest_commit,
                "tasks_by_tags": tasks_by_tags,
            },
        )
        return context
