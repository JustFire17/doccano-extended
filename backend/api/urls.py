from django.urls import path, include

from .views import TaskStatus, HealthCheckView

urlpatterns = [
    path(route="tasks/status/<task_id>", view=TaskStatus.as_view(), name="task_status"),
    path(route="health/", view=HealthCheckView.as_view(), name="health_check"),
]