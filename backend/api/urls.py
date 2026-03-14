from django.urls import path

from .views import HealthCheckView, TaskStatus

urlpatterns = [
    path(route="tasks/status/<task_id>", view=TaskStatus.as_view(), name="task_status"),
    path(route="health/", view=HealthCheckView.as_view(), name="health_check"),
]
