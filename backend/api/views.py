from django.contrib.auth.models import User
from celery.result import AsyncResult
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class TaskStatus(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        task = AsyncResult(kwargs["task_id"])
        ready = task.ready()
        error = ready and not task.successful()

        return Response(
            {
                "ready": ready,
                "result": task.result if ready and not error else None,
                "error": {"text": str(task.result)} if error else None,
            }
        )


class HealthCheckView(APIView):
    """
    Simple health check view that returns a 200 response
    Used by Docker healthcheck to verify the service is running
    """
    permission_classes = ()  # No permission required

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})