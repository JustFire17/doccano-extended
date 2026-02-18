from rest_framework.permissions import BasePermission
from projects.models import Project
from django.shortcuts import get_object_or_404


class CanEditLabel(BasePermission):
    def __init__(self, queryset):
        super().__init__()
        self.queryset = queryset

    def has_permission(self, request, view):
        project = get_object_or_404(Project, pk=view.kwargs["project_id"])
        
        # Não permitir edições se o projeto estiver fechado
        if project.closed:
            return False

        if request.user.is_superuser:
            return True

        annotation_id = view.kwargs.get("annotation_id")
        return self.queryset.filter(id=annotation_id, user=request.user).exists()
