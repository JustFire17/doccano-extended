from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from examples.filters import ExampleFilter
from examples.models import Example
from examples.serializers import ExampleSerializer
from projects.models import Member, Project
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly

from rest_framework.exceptions import NotFound
from django.db.models import Count, F
from rest_framework.views import APIView


class ExampleList(generics.ListCreateAPIView):
    serializer_class = ExampleSerializer
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ("created_at", "updated_at", "score")
    search_fields = ("text", "filename")
    model = Example
    filterset_class = ExampleFilter

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"])

    def get_queryset(self):
        member = get_object_or_404(Member, project=self.project, user=self.request.user)
        
        # Get the original project (where examples are stored)
        original_project = self.project.original_project or self.project
        
        if member.is_admin():
            return self.model.objects.filter(project=original_project)

        queryset = self.model.objects.filter(project=original_project, assignments__assignee=self.request.user)
        if self.project.random_order:
            queryset = queryset.order_by("assignments__id")
        return queryset

    def perform_create(self, serializer):
        # Create examples in the original project (where they should be stored)
        original_project = self.project.original_project or self.project
        serializer.save(project=original_project)

    def delete(self, request, *args, **kwargs):
        # Delete examples from the original project (where they are stored)
        original_project = self.project.original_project or self.project
        queryset = original_project.examples
        delete_ids = request.data["ids"]
        if delete_ids:
            queryset.filter(pk__in=delete_ids).delete()
        else:
            queryset.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExampleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Example.objects.all()
    serializer_class = ExampleSerializer
    lookup_url_kwarg = "example_id"
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
