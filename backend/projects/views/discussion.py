from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from projects.models import Discussion, DiscussionMessage, Project
from projects.permissions import IsProjectAdmin, IsProjectMember
from projects.serializers import DiscussionSerializer, DiscussionMessageSerializer


class DiscussionList(generics.ListCreateAPIView):
    serializer_class = DiscussionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-updated_at"]
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_queryset(self):
        """Get discussions from all versions of the project to show complete history"""
        from django.db import models
        
        current_project = get_object_or_404(Project, id=self.kwargs["project_id"])
        
        # Get the original project to find all versions
        original_project = current_project.original_project or current_project
        
        # Get all versions of this project (including the original)
        all_project_versions = Project.objects.filter(
            models.Q(id=original_project.id) | models.Q(original_project=original_project)
        )
        
        # Get discussions from all versions
        return Discussion.objects.filter(
            project__in=all_project_versions
        ).select_related('project', 'created_by')

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs["project_id"],
            created_by=self.request.user
        )


class DiscussionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DiscussionSerializer
    lookup_url_kwarg = "discussion_id"
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_queryset(self):
        """Get discussions from all versions of the project to show complete history"""
        from django.db import models
        
        current_project = get_object_or_404(Project, id=self.kwargs["project_id"])
        
        # Get the original project to find all versions
        original_project = current_project.original_project or current_project
        
        # Get all versions of this project (including the original)
        all_project_versions = Project.objects.filter(
            models.Q(id=original_project.id) | models.Q(original_project=original_project)
        )
        
        # Get discussions from all versions
        return Discussion.objects.filter(
            project__in=all_project_versions
        ).select_related('project', 'created_by')


class DiscussionMessageList(generics.ListCreateAPIView):
    serializer_class = DiscussionMessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["created_at"]
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_queryset(self):
        """Get messages from discussions across all versions of the project"""
        from django.db import models
        
        current_project = get_object_or_404(Project, id=self.kwargs["project_id"])
        
        # Get the original project to find all versions
        original_project = current_project.original_project or current_project
        
        # Get all versions of this project (including the original)
        all_project_versions = Project.objects.filter(
            models.Q(id=original_project.id) | models.Q(original_project=original_project)
        )
        
        return DiscussionMessage.objects.filter(
            discussion_id=self.kwargs["discussion_id"],
            discussion__project__in=all_project_versions
        )

    def perform_create(self, serializer):
        """Create a message in a discussion from any version of the project"""
        from django.db import models
        
        current_project = get_object_or_404(Project, id=self.kwargs["project_id"])
        
        # Get the original project to find all versions
        original_project = current_project.original_project or current_project
        
        # Get all versions of this project (including the original)
        all_project_versions = Project.objects.filter(
            models.Q(id=original_project.id) | models.Q(original_project=original_project)
        )
        
        discussion = get_object_or_404(
            Discussion,
            id=self.kwargs["discussion_id"],
            project__in=all_project_versions
        )
        serializer.save(
            discussion=discussion,
            sender=self.request.user
        )


class DiscussionMessageDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DiscussionMessageSerializer
    lookup_url_kwarg = "message_id"
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_queryset(self):
        """Get messages from discussions across all versions of the project"""
        from django.db import models
        
        current_project = get_object_or_404(Project, id=self.kwargs["project_id"])
        
        # Get the original project to find all versions
        original_project = current_project.original_project or current_project
        
        # Get all versions of this project (including the original)
        all_project_versions = Project.objects.filter(
            models.Q(id=original_project.id) | models.Q(original_project=original_project)
        )
        
        return DiscussionMessage.objects.filter(
            discussion_id=self.kwargs["discussion_id"],
            discussion__project__in=all_project_versions
        )
    
    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        # Only the sender or a project admin can delete a message
        if message.sender != request.user and not IsProjectAdmin().has_permission(request, self):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs) 