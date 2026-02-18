from django.conf import settings
from django.db import transaction, models
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, views, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from projects.models import PerspectiveMember, Project, ManualDiscrepancy, DiscrepancyLabelStat, Perspective, PerspectiveProject, Rule, RuleVote, DiscrepancyComment
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly
from projects.serializers import PerspectiveMemberSerializer, ProjectPolymorphicSerializer, ManualDiscrepancySerializer, PerspectiveSerializer, RuleSerializer, DiscrepancyCommentSerializer

from rest_framework.views import APIView
from examples.models import Example
from labels.models import Category
from django.db.models import Count
from rest_framework.exceptions import NotFound
import datetime

from django.http import HttpResponse

class ProjectList(generics.ListCreateAPIView):
    serializer_class = ProjectPolymorphicSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ["name", "created_at", "created_by", "project_type"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [
                IsAuthenticated,
            ]
        else:
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        return Project.objects.filter(role_mappings__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        project.add_admin()

    def delete(self, request, *args, **kwargs):
        delete_ids = request.data["ids"]
        projects = Project.objects.filter(
            role_mappings__user=self.request.user,
            pk__in=delete_ids,
        )
        
        # Get all versions of the projects to be deleted
        all_versions_to_delete = []
        for project in projects:
            # Get the original project
            original_project = project.original_project or project
            
            # Get all versions of this project
            versions = Project.objects.filter(
                models.Q(id=original_project.id) | 
                models.Q(original_project=original_project)
            )
            all_versions_to_delete.extend(versions)
        
        # Delete all versions
        for version in all_versions_to_delete:
            version.delete()
            
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectPolymorphicSerializer
    lookup_url_kwarg = "project_id"
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]


class CloseProject(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)    
        project.closed = True
        project.save()
        
        return Response(
            {"message": "Project closed successfully"},
            status=status.HTTP_200_OK
        )
    
class ReopenProject(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)    
        
        # Create a new version of the project
        new_version = project.create_new_version()
        
        serializer = ProjectPolymorphicSerializer(new_version)
        return Response(
            {
                "message": "Project reopened successfully",
                "new_version": serializer.data
            },
            status=status.HTTP_200_OK
        )


class CloneProject(views.APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        cloned_project = project.clone()
        serializer = ProjectPolymorphicSerializer(cloned_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CreateRuleWithItems(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        rules = []
        for item in request.data.get('items', []):
            rule = Rule.objects.create(
                name=item.get('name'),
                description=item.get('description'),
                project=project
            )
            rules.append(rule)

        serializer = RuleSerializer(rules, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CreatePerspectiveWithItems(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, project_id):
        # Check if a perspective project with this name already exists
        if PerspectiveProject.objects.filter(name=request.data.get('name')).exists():
            return Response(
                {"error": "A perspective with this name already exists. Please choose a different name."},
                status=status.HTTP_400_BAD_REQUEST
            )

        perspective_project = PerspectiveProject.objects.create(
            name=request.data.get('name'),
            created_by=request.user  # Garantir que o usuário atual seja registrado como criador
        )

        perspectives = []
        for item in request.data.get('items', []):
            perspective = Perspective.objects.create(
                name=item.get('name'),
                type=item.get('type'),
                options=item.get('options', ''),
                perspective_project=perspective_project
            )
            perspectives.append(perspective)

        serializer = PerspectiveSerializer(perspectives, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class AssociatePerspectiveView(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        perspective_project_id = request.data.get('perspective_project_id')
        
        if not perspective_project_id:
            return Response(
                {"error": "perspective_project_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        perspective_project = get_object_or_404(PerspectiveProject, id=perspective_project_id)
        
        # Update project with associated perspective
        project.perspective_associated = perspective_project
        project.save()
        
        return Response(
            {"message": f"Perspective '{perspective_project.name}' associated successfully with project '{project.name}'"},
            status=status.HTTP_200_OK
        )

    def delete(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        if not project.perspective_associated:
            return Response(
                {"error": "No perspective is currently associated with this project"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove association
        project.perspective_associated = None
        project.save()
        
        return Response(
            {"message": "Perspective association removed successfully"},
            status=status.HTTP_200_OK
        )    


class FillPerspectives(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        user = request.user
        project = get_object_or_404(Project, id=project_id)
        
        # Check if project has an associated perspective project
        if not project.perspective_associated:
            return Response(
                {"error": "This project doesn't have an associated perspective set."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        member = get_object_or_404(project.role_mappings, user=user)
        data = request.data  # Expects a dictionary { perspective_id: value }

        for perspective_id, value in data.items():
            # Get perspective from the associated perspective project
            perspective = get_object_or_404(
                Perspective, 
                id=perspective_id, 
                perspective_project=project.perspective_associated
            )
            
            PerspectiveMember.objects.update_or_create(
                member=member,
                perspective=perspective,
                defaults={"value": value}
            )

        return Response({"message": "Values saved successfully."}, status=status.HTTP_200_OK)
    
class GetFilledPerspectives(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        user = request.user
        project = get_object_or_404(Project, id=project_id)
        
        # Check if project has an associated perspective project
        if not project.perspective_associated:
            return Response([], status=status.HTTP_200_OK)
            
        member = get_object_or_404(project.role_mappings, user=user)

        # Only get perspective members for perspectives that belong to the project's perspective project
        perspective_members = PerspectiveMember.objects.filter(
            member=member,
            perspective__perspective_project=project.perspective_associated
        )
        
        serializer = PerspectiveMemberSerializer(perspective_members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetAllFilledValues(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Get all versions of this project (current and previous versions)
        original_project = project.original_project or project
        all_project_versions = Project.objects.filter(
            models.Q(id=original_project.id) | 
            models.Q(original_project=original_project)
        ).values_list('id', flat=True)
        
        # Get all perspective members for ALL project versions
        perspective_members = PerspectiveMember.objects.filter(
            member__project_id__in=all_project_versions
        ).select_related('perspective')
        
        # Group values by perspective
        result = {}
        for member in perspective_members:
            if member.perspective_id not in result:
                result[member.perspective_id] = set()
            result[member.perspective_id].add(member.value)
        
        # Convert sets to lists
        for perspective_id in result:
            result[perspective_id] = list(result[perspective_id])
            
        return Response(result, status=status.HTTP_200_OK)

class GetUsersWithValue(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        perspective_id = request.query_params.get('perspective_id')
        value = request.query_params.get('value')

        if not perspective_id or not value:
            return Response(
                {"error": "perspective_id and value are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get all versions of this project (current and previous versions)
        original_project = project.original_project or project
        all_project_versions = Project.objects.filter(
            models.Q(id=original_project.id) | 
            models.Q(original_project=original_project)
        ).values_list('id', flat=True)

        # Get all members who have this value for this perspective across ALL project versions
        perspective_members = PerspectiveMember.objects.filter(
            member__project_id__in=all_project_versions,
            perspective_id=perspective_id,
            value=value
        ).select_related('member__user')

        # Extract usernames
        usernames = [member.member.user.username for member in perspective_members]
        return Response(usernames, status=status.HTTP_200_OK)

class AllPerspectivesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        # Buscar apenas as PerspectiveProjects criadas pelo usuário atual
        perspective_projects = PerspectiveProject.objects.filter(created_by=request.user)
        result = []
        
        for perspective_project in perspective_projects:
            # Buscar todas as perspectivas para este PerspectiveProject
            perspectives = Perspective.objects.filter(perspective_project=perspective_project)
            items = []
            
            for perspective in perspectives:
                items.append({
                    "id": perspective.id,
                    "name": perspective.name,
                    "type": perspective.type,
                    "options": perspective.options
                })
            
            # Buscar todos os projetos associados a este PerspectiveProject
            associated_projects = perspective_project.projects.all()
            associated_projects_list = [
                {"id": project.id, "name": project.name, "version": project.version} for project in associated_projects
            ]

            perspective_data = {
                "id": perspective_project.id,
                "name": perspective_project.name,
                "items": items,
                "associated_projects": associated_projects_list,
                "created_at": perspective_project.created_at.isoformat() if perspective_project.created_at else None,
                "updated_at": perspective_project.updated_at.isoformat() if perspective_project.updated_at else None,
                "creator": perspective_project.created_by.username if perspective_project.created_by else None
            }
            result.append(perspective_data)
        
        return Response(result, status=status.HTTP_200_OK)

class PerspectiveList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        from django.db import DatabaseError
        try:
            project = get_object_or_404(Project, id=project_id)
            # Check if project has an associated perspective_project
            if not project.perspective_associated:
                return Response([], status=status.HTTP_200_OK)
            # Get all perspectives for this project's perspective_project
            perspectives = Perspective.objects.filter(perspective_project=project.perspective_associated)
            results = []
            for perspective in perspectives:
                results.append({
                    "id": perspective.id,
                    "name": perspective.name,
                    "type": perspective.type,
                    "options": perspective.options,
                    "project": project_id,
                    "perspective_project": project.perspective_associated.id
                })
            return Response({"results": results}, status=status.HTTP_200_OK)
        except DatabaseError:
            return Response(
                {"detail": "Sorry, we couldn't load the perspectives right now. Please try again in a few moments."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, project_id, perspective_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Check if project has an associated perspective_project
        if not project.perspective_associated:
            return Response(
                {"error": "No perspective project associated with this project"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check if user is the creator of the perspective
        if project.perspective_associated.created_by != request.user:
            return Response(
                {"error": "You don't have permission to delete these perspectives"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Get the perspective to delete
        perspective = get_object_or_404(
            Perspective,
            id=perspective_id,
            perspective_project=project.perspective_associated
        )
        
        # Delete the perspective
        perspective.delete()
        
        return Response(
            {"message": f"Perspective '{perspective.name}' deleted successfully"},
            status=status.HTTP_200_OK
        )

class DeletePerspectiveTotal(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def delete(self, request, project_id, perspective_id):
        # Get the perspective project to delete
        perspective_project = get_object_or_404(PerspectiveProject, id=perspective_id)
        
        # Check if this perspective project is associated with any project
        if Project.objects.filter(perspective_associated=perspective_project).exists():
            return Response(
                {"error": "Cannot delete this perspective project because it is associated with one or more projects. Please dissociate it from all projects first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete the perspective project (this will cascade delete all associated perspectives)
        perspective_project.delete()
        
        return Response(
            {"message": f"Perspective '{perspective_project.name}' and all its items deleted successfully"},
            status=status.HTTP_200_OK
        )

class DiscrepancyAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        discrepancy_threshold = project.discrepancy_percentage
        
        # Get the original project (where examples are stored)
        original_project = project.original_project or project
        examples = Example.objects.filter(project_id=original_project.id)

        # Buscar todas as discrepâncias manuais associadas ao projeto
        manual_discrepancies = ManualDiscrepancy.objects.filter(project_id=project_id)
        manual_examples = set(md.example_id for md in manual_discrepancies)

        discrepancies = []
        for example in examples:
            # Filter annotations by the current project version
            labels = example.categories.filter(project_version=project.version).values('label', 'label__text').annotate(count=Count('label'))
            total_labels = sum(label['count'] for label in labels)

            if total_labels > 0:
                percentages = {label['label__text']: (label['count'] / total_labels) * 100 for label in labels}
                max_percentage = max(percentages.values())

                if max_percentage < discrepancy_threshold:
                    # Determinar o status
                    if example.id in manual_examples:
                        status = 'Reported'
                    else:
                        status = 'Not Reported'
                    discrepancies.append({
                        "id": example.id,
                        "text": example.text,
                        "percentages": percentages,
                        "status": status,
                    })

        return Response({"discrepancies": discrepancies})


class AnnotationsByUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        examples = Example.objects.filter(project_id=project_id)

        if not examples.exists():
            raise NotFound("No examples found for this project.")

        # Get all unique users who have made annotations
        users = set()
        for example in examples:
            users.update(example.categories.values_list('user__username', flat=True))
        users = sorted(list(users))

        items = []
        for example in examples:
            # Get all annotations for this example
            annotations = example.categories.select_related('user', 'label')
            
            # Create a row with text and annotations for each user
            row = {
                "id": example.id,
                "text": example.text,
            }
            
            # Add each user's annotation as a separate field
            for user in users:
                user_annotation = annotations.filter(user__username=user).first()
                row[user] = user_annotation.label.text if user_annotation else None

            items.append(row)

        return Response({
            "items": items,
            "users": users
        }, content_type='application/json')

# This class defines API endpoints for retrieving and creating manual discrepancies associated with a
# specific project.
class ManualDiscrepancyListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        # Get all manual discrepancies associated with the project
        discrepancies = ManualDiscrepancy.objects.filter(project_id=project_id)
        serializer = ManualDiscrepancySerializer(discrepancies, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        # Check if a discrepancy already exists for this example
        example_id = request.data.get('example')
        if ManualDiscrepancy.objects.filter(project_id=project_id, example_id=example_id).exists():
            return Response(
                {"error": "A discrepancy has already been reported for this dataset."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if there are at least 2 different annotations
        label_stats = request.data.get("label_stats", [])
        total_votes = sum(stat["vote_count"] for stat in label_stats)
        if total_votes < 2:
            return Response(
                {"error": "Unable to report discrepancy. A minimum of two distinct labels is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data["project"] = project_id
        data["reported_by"] = request.user.id  # Who is reporting the discrepancy

        # Validate and save the manual discrepancy
        serializer = ManualDiscrepancySerializer(data=data, context={"request": request})
        if serializer.is_valid():
            discrepancy = serializer.save()

            # Add the label statistics associated with the discrepancy
            for stat in label_stats:
                DiscrepancyLabelStat.objects.create(
                    discrepancy=discrepancy,
                    label_text=stat["label_text"],
                    vote_count=stat["vote_count"],
                    percentage=stat["percentage"]
                )

            return Response(ManualDiscrepancySerializer(discrepancy).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LabelStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, example_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Get the original project (where examples are stored)
        original_project = project.original_project or project
        
        # Find the example in the original project
        example = get_object_or_404(Example, id=example_id, project_id=original_project.id)

        # Filter annotations by the current project version
        annotations = example.categories.filter(project_version=project.version).values('label__text').annotate(count=Count('label'))
        total = sum(a['count'] for a in annotations)

        result = {}
        for a in annotations:
            label_text = a['label__text']
            count = a['count']
            percentage = (count / total * 100) if total > 0 else 0
            result[label_text] = {
                'count': count,
                'percentage': percentage
            }

        return Response(result, status=status.HTTP_200_OK)


class AnnotatorReportView(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Get all versions of this project (current and previous versions)
        original_project = project.original_project or project
        all_project_versions = Project.objects.filter(
            models.Q(id=original_project.id) | 
            models.Q(original_project=original_project)
        ).values_list('id', flat=True)
        
        # Parse query parameters
        start_date = request.query_params.get('dateStart')
        end_date = request.query_params.get('dateEnd')
        perspective_ids = request.query_params.get('perspectiveId')
        perspective_values = request.query_params.get('perspectiveValue')
        username = request.query_params.get('username')
        example_id = request.query_params.get('exampleId')
        project_version = request.query_params.get('projectVersion')
        label_ids = request.query_params.get('labelIds')
        
        # Base queryset for annotations (categories) from ALL project versions
        # Since examples are shared, we need to get annotations from all versions
        annotations = Category.objects.filter(example__project_id=original_project.id)\
            .select_related('user', 'example', 'label')\
            .order_by('-created_at')
        
        # Apply date filters if provided
        if start_date:
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                annotations = annotations.filter(created_at__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.combine(end_date, datetime.time.max)
                annotations = annotations.filter(created_at__lte=end_date)
            except ValueError:
                pass
        
        # Apply example filter if provided
        if example_id:
            try:
                example_ids = [int(eid.strip()) for eid in example_id.split(',') if eid.strip()]
                if example_ids:
                    annotations = annotations.filter(example_id__in=example_ids)
            except ValueError:
                pass
        
        # Apply project version filter if provided
        if project_version:
            try:
                project_versions = [int(v.strip()) for v in project_version.split(',') if v.strip()]
                if project_versions:
                    annotations = annotations.filter(project_version__in=project_versions)
            except ValueError:
                pass
        
        # Apply username filter if provided
        if username:
            usernames = [u.strip() for u in username.split(',') if u.strip()]
            if usernames:
                annotations = annotations.filter(user__username__in=usernames)
        
        # Apply perspective filters if provided
        if perspective_ids and perspective_values and project.perspective_associated:
            try:
                # Parse multiple perspective IDs and values
                perspective_id_list = [int(pid.strip()) for pid in perspective_ids.split(',') if pid.strip()]
                perspective_value_list = [pv.strip() for pv in perspective_values.split(',') if pv.strip()]
                
                if perspective_id_list and perspective_value_list:
                    # Find members that match any combination of perspective_id and perspective_value
                    # Check across all project versions
                    perspective_members = PerspectiveMember.objects.filter(
                        perspective_id__in=perspective_id_list,
                        value__in=perspective_value_list,
                        member__project_id__in=all_project_versions
                    ).values_list('member__user_id', flat=True).distinct()
                    
                    annotations = annotations.filter(user_id__in=perspective_members)
            except (ValueError, TypeError):
                pass
        
        # Prepare the response data
        result = []
        unique_examples = {}  # Para filtro de examples únicos baseado em ID
        project_versions = set()  # Para filtro de versões
        
        for annotation in annotations:
            # Adicionar versão à lista
            project_versions.add(annotation.project_version)
            
            # Adicionar example único baseado no ID
            if annotation.example.id not in unique_examples:
                example_text = annotation.example.text[:50] + '...' if len(annotation.example.text) > 50 else annotation.example.text
                unique_examples[annotation.example.id] = {
                    'text': annotation.example.text,
                    'display_text': example_text,
                    'id': annotation.example.id
                }
            
            result.append({
                'id': annotation.id,
                'username': annotation.user.username,
                'created_at': annotation.created_at.isoformat(),
                'type': annotation.example.project.project_type,
                'example_id': annotation.example.id,
                'example_text': annotation.example.text[:200] + '...' if len(annotation.example.text) > 200 else annotation.example.text,
                'label_id': annotation.label.id,
                'label_text': annotation.label.text,
                'backgroundColor': annotation.label.background_color,
                'project_version': annotation.project_version
            })
        
        # Preparar dados de filtros
        unique_examples_list = list(unique_examples.values())
        project_versions_list = sorted(list(project_versions))
        
        return Response({
            'annotations': result,
            'unique_examples': unique_examples_list,
            'project_versions': project_versions_list
        }, status=status.HTTP_200_OK)


class AnnotationStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Get query parameters matching frontend parameter names
        annotation_ids = request.query_params.get('exampleId', '').split(',') if request.query_params.get('exampleId') else []
        perspective_ids = request.query_params.get('perspectiveId', '').split(',') if request.query_params.get('perspectiveId') else []
        perspective_values = request.query_params.get('perspectiveValue', '').split(',') if request.query_params.get('perspectiveValue') else []

        original_project = project.original_project or project
        examples = Example.objects.filter(project_id=original_project.id)
        if annotation_ids:
            annotation_ids = [int(id) for id in annotation_ids if id.strip()]
            if annotation_ids:
                examples = examples.filter(id__in=annotation_ids)

        users_to_consider = None
        if perspective_ids and perspective_values:
            try:
                perspective_ids = [int(id) for id in perspective_ids if id.strip()]
                perspective_values = [val for val in perspective_values if val.strip()]
                
                if perspective_ids and perspective_values:
                    perspective_members = PerspectiveMember.objects.filter(
                        perspective_id__in=perspective_ids,
                        value__in=perspective_values,
                        member__project=project
                    )
                    member_perspective_count = {}
                    for pm in perspective_members:
                        if pm.member_id not in member_perspective_count:
                            member_perspective_count[pm.member_id] = set()
                        member_perspective_count[pm.member_id].add(pm.perspective_id)
                    valid_members = [
                        member_id
                        for member_id, perspectives in member_perspective_count.items()
                        if len(perspectives) == len(set(perspective_ids))
                    ]
                    if valid_members:
                        users_to_consider = PerspectiveMember.objects.filter(
                            member_id__in=valid_members
                        ).values_list('member__user_id', flat=True).distinct()
            except (ValueError, TypeError) as e:
                print(f"Error processing perspective filters: {e}")
                pass

        result = []
        discrepancy_threshold = project.discrepancy_percentage
        manual_discrepancies = ManualDiscrepancy.objects.filter(project_id=project.id)
        manual_examples = set(md.example_id for md in manual_discrepancies)
        discrepancies_auto = set()
        for example in examples:
            labels = example.categories.filter(
                project_version=project.version
            ).values('label', 'label__text').annotate(count=Count('label'))
            total_labels = sum(label['count'] for label in labels)
            if total_labels > 0:
                percentages = {label['label__text']: (label['count'] / total_labels) * 100 for label in labels}
                max_percentage = max(percentages.values())
                if max_percentage < discrepancy_threshold:
                    discrepancies_auto.add(example.id)
        
        for example in examples:
            all_labels = example.categories.filter(
                project_version=project.version
            ).select_related('label').values(
                'label__id',
                'label__text',
                'label__background_color'
            ).annotate(count=Count('label')).distinct()
            
            total_all_labels = sum(label['count'] for label in all_labels)
            
            categories_query = example.categories.filter(project_version=project.version).select_related('label')
            
            if users_to_consider is not None:
                categories_query = categories_query.filter(user_id__in=users_to_consider)
            
            filtered_labels = categories_query.values(
                'label__id',
                'label__text',
                'label__background_color'
            ).annotate(count=Count('label')).distinct()

            total_filtered_labels = sum(label['count'] for label in filtered_labels)

            if total_filtered_labels > 0:
                others_count = total_all_labels - total_filtered_labels
                
                labels_result = [{
                    'id': label['label__id'],
                    'text': label['label__text'],
                    'backgroundColor': label['label__background_color'],
                    'percentage': (label['count'] / total_all_labels * 100)
                } for label in filtered_labels]
                
                if others_count > 0:
                    labels_result.append({
                        'id': -1,
                        'text': 'Others',
                        'backgroundColor': '#757575',
                        'percentage': (others_count / total_all_labels * 100)
                    })

                is_discrepancy = example.id in discrepancies_auto
                if is_discrepancy:
                    discrepancy_status = 'Reported' if example.id in manual_examples else 'Not Reported'
                else:
                    discrepancy_status = None
                users_result = list(categories_query.values(
                    'user__id',
                    'user__username'
                ).distinct())
                
                first_annotation = categories_query.first()
                version = first_annotation.project_version if first_annotation else None
                created_at = first_annotation.created_at if first_annotation else None

                result.append({
                    'id': f"{example.id}",
                    'example_id': example.id,
                    'text': example.text,
                    'labels': labels_result,
                    'version': version,
                    'users': [{'id': u['user__id'], 'username': u['user__username']} for u in users_result],
                    'created_at': created_at.isoformat() if created_at else None,
                    'discrepancy': is_discrepancy,
                    'discrepancy_status': discrepancy_status
                })

        return Response({
            'annotations': result
        })

class AllVersionsStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Get query parameters
        annotation_ids = request.query_params.getlist('annotation_ids', [])
        perspective_ids = request.query_params.getlist('perspective_ids', [])
        perspective_values = request.query_params.getlist('perspective_values', [])
        version_ids = request.query_params.getlist('version_ids', [])

        # Get all versions to consider and order them by version number
        if version_ids:
            versions = Project.objects.filter(id__in=version_ids).order_by('version')
        else:
            # If no versions specified, use current project
            versions = [project]

        # Base query for examples - get examples from the original project
        original_project = project.original_project or project
        examples = Example.objects.filter(project_id=original_project.id)
        
        # Apply annotation filter if provided
        if annotation_ids:
            examples = examples.filter(id__in=annotation_ids)
            
        # Filter by perspectives if provided
        users_to_consider = None
        if perspective_ids and perspective_values:
            perspective_members = PerspectiveMember.objects.filter(
                perspective_id__in=perspective_ids,
                value__in=perspective_values,
                member__project__in=versions
            )
            
            member_perspective_count = {}
            for pm in perspective_members:
                if pm.member_id not in member_perspective_count:
                    member_perspective_count[pm.member_id] = set()
                member_perspective_count[pm.member_id].add(pm.perspective_id)
            
            valid_members = [
                member_id 
                for member_id, perspectives in member_perspective_count.items()
                if len(perspectives) == len(set(perspective_ids))
            ]
            
            if valid_members:
                users_to_consider = PerspectiveMember.objects.filter(
                    member_id__in=valid_members
                ).values_list('member__user_id', flat=True).distinct()

        # Get annotations with their labels, organized by version
        result = []
        for version in versions:
            # Buscar discrepâncias automáticas e manuais para esta versão
            discrepancy_threshold = version.discrepancy_percentage
            manual_discrepancies = ManualDiscrepancy.objects.filter(project_id=version.id)
            manual_examples = set(md.example_id for md in manual_discrepancies)
            discrepancies_auto = set()
            
            # Get annotations for this version
            version_annotations = examples.filter(
                categories__project_version=version.version
            ).distinct()
            
            for example in version_annotations:
                labels = example.categories.filter(
                    project_version=version.version
                ).values('label', 'label__text').annotate(count=Count('label'))
                
                total_labels = sum(label['count'] for label in labels)
                if total_labels > 0:
                    percentages = {label['label__text']: (label['count'] / total_labels) * 100 for label in labels}
                    max_percentage = max(percentages.values())
                    if max_percentage < discrepancy_threshold:
                        discrepancies_auto.add(example.id)
            
            version_data = {
                'version_id': version.id,
                'version_number': version.version,
                'is_current_version': version.id == project.id,  # Only mark as current if it's the current project
                'annotations': []
            }
            
            for example in version_annotations:
                # Get all labels for this example in this version
                all_labels = example.categories.filter(
                    project_version=version.version
                ).select_related('label').values(
                    'label__id',
                    'label__text',
                    'label__background_color'
                ).annotate(count=Count('label')).distinct()
                
                total_all_labels = sum(label['count'] for label in all_labels)
                
                # Base query for filtered categories
                categories_query = example.categories.filter(project_version=version.version).select_related('label')
                
                if users_to_consider is not None:
                    categories_query = categories_query.filter(user_id__in=users_to_consider)
                
                filtered_labels = categories_query.values(
                    'label__id',
                    'label__text',
                    'label__background_color'
                ).annotate(count=Count('label')).distinct()

                total_filtered_labels = sum(label['count'] for label in filtered_labels)

                if total_filtered_labels > 0:
                    others_count = total_all_labels - total_filtered_labels
                    
                    labels_result = [{
                        'id': label['label__id'],
                        'text': label['label__text'],
                        'backgroundColor': label['label__background_color'],
                        'percentage': (label['count'] / total_all_labels * 100)
                    } for label in filtered_labels]
                    
                    if others_count > 0:
                        labels_result.append({
                            'id': -1,
                            'text': 'Others',
                            'backgroundColor': '#757575',
                            'percentage': (others_count / total_all_labels * 100)
                        })

                    # Adicionar info de discrepância
                    is_discrepancy = example.id in discrepancies_auto
                    if is_discrepancy:
                        discrepancy_status = 'Reported' if example.id in manual_examples else 'Not Reported'
                    else:
                        discrepancy_status = None

                    version_data['annotations'].append({
                        'id': example.id,
                        'text': example.text,
                        'labels': labels_result,
                        'discrepancy': is_discrepancy,
                        'discrepancy_status': discrepancy_status
                    })
            
            if version_data['annotations']:
                result.append(version_data)

        # Sort the result by version number
        result.sort(key=lambda x: x['version_number'])

        return Response({
            'versions': result
        })
        

class RuleListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RuleSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsProjectAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Rule.objects.filter(project_id=project_id)

    def list(self, request, *args, **kwargs):
        from django.db import DatabaseError
        try:
            return super().list(request, *args, **kwargs)
        except DatabaseError:
            return Response(
                {"detail": "Sorry, we couldn't load the rules right now. Please try again in a few moments."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        # Set the rule version to the project version when creating a new rule
        rule = serializer.save(project=project, version=project.version)
        print(f"Created rule: {rule}")  # Debug log

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class RuleDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RuleSerializer
    lookup_url_kwarg = 'rule_id'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsProjectAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Rule.objects.filter(project_id=project_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class RuleVoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, rule_id):
        try:
            rule = get_object_or_404(Rule, id=rule_id, project_id=project_id)
            project = get_object_or_404(Project, id=project_id)
            
            # Check if the rule belongs to the current version of the project
            if rule.version != project.version:
                return Response(
                    {"detail": "Não é possível votar em regras de versões anteriores do projeto."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if voting is closed
            if rule.voting_closed:
                return Response(
                    {"detail": "Voting for this rule is already closed."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already voted
            existing_vote = RuleVote.objects.filter(rule=rule, user=request.user).first()
            is_upvote = request.data.get('is_upvote', True)
            
            if existing_vote:
                # Se o usuário já votou da mesma forma, remove o voto
                if existing_vote.is_upvote == is_upvote:
                    existing_vote.delete()
                else:
                    # Se votou diferente, atualiza o voto
                    existing_vote.is_upvote = is_upvote
                    existing_vote.save()
            else:
                # Create new vote
                RuleVote.objects.create(
                    rule=rule,
                    user=request.user,
                    is_upvote=is_upvote
                )
            
            # Return updated rule data
            serializer = RuleSerializer(rule, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            if hasattr(e, 'message'):
                return Response({'detail': str(e.message)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'Database unavailable. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ProjectVersionsList(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        # Get the original project
        original_project = project.original_project or project
        
        # Get all versions of the project
        versions = Project.objects.filter(
            models.Q(id=original_project.id) | 
            models.Q(original_project=original_project)
        ).order_by('version')
        
        serializer = ProjectPolymorphicSerializer(versions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class CloseRuleVote(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, project_id, rule_id):
        try:
            rule = get_object_or_404(Rule, id=rule_id, project_id=project_id)
            rule.voting_closed = True
            rule.save()
            
            # Return updated rule data
            serializer = RuleSerializer(rule, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            if hasattr(e, 'message'):
                return Response({'detail': str(e.message)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'Database unavailable. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ReopenRuleVote(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, project_id, rule_id):
        try:
            rule = get_object_or_404(Rule, id=rule_id, project_id=project_id)
            rule.voting_closed = False
            
            # Update voting end date and time if provided
            if 'voting_end_date' in request.data:
                rule.voting_end_date = request.data['voting_end_date']
            if 'voting_end_time' in request.data:
                rule.voting_end_time = request.data['voting_end_time']
            
            rule.save()
            
            # Return updated rule data
            serializer = RuleSerializer(rule, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            if hasattr(e, 'message'):
                return Response({'detail': str(e.message)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'Database unavailable. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AnnotationLabelTableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        from django.db import DatabaseError
        try:
            project = get_object_or_404(Project, id=project_id)
            original_project = project.original_project or project
            examples = Example.objects.filter(project_id=original_project.id)

            # Obter todas as labels possíveis no projeto
            all_labels = set()
            for example in examples:
                labels = example.categories.filter(project_version=project.version).values_list('label__text', flat=True)
                all_labels.update(labels)
            all_labels = sorted(list(all_labels))

            # Cálculo de discrepância
            discrepancy_threshold = project.discrepancy_percentage
            manual_discrepancies = ManualDiscrepancy.objects.filter(project_id=project.id)
            manual_examples = set(md.example_id for md in manual_discrepancies)
            discrepancies_auto = set()
            for example in examples:
                labels = example.categories.filter(project_version=project.version).values('label', 'label__text').annotate(count=Count('label'))
                total_labels = sum(label['count'] for label in labels)
                if total_labels > 0:
                    percentages = {label['label__text']: (label['count'] / total_labels) * 100 for label in labels}
                    max_percentage = max(percentages.values())
                    if max_percentage < discrepancy_threshold:
                        discrepancies_auto.add(example.id)

            # Montar a tabela
            table = []
            for example in examples:
                row = {
                    'id': example.id,
                    'text': example.text,
                }
                # Contagem de labels
                label_counts = {label: 0 for label in all_labels}
                labels = example.categories.filter(project_version=project.version).values('label__text').annotate(count=Count('label'))
                for label in labels:
                    label_counts[label['label__text']] = label['count']
                row['labels'] = label_counts
                # Discrepância e reportado
                is_discrepancy = example.id in discrepancies_auto
                is_reported = example.id in manual_examples
                row['discrepancy'] = is_discrepancy
                row['reported'] = is_reported
                # Adicionar valores de perspetiva igual ao Annotation Statistics
                # Buscar utilizadores que anotaram este exemplo
                user_ids = example.categories.filter(project_version=project.version).values_list('user_id', flat=True).distinct()
                perspectives_dict = {}
                if user_ids:
                    # Usar o primeiro utilizador que anotou
                    user_id = user_ids[0]
                    member = project.role_mappings.filter(user_id=user_id).first()
                    if member:
                        member_perspectives = PerspectiveMember.objects.filter(member=member)
                        for pm in member_perspectives:
                            perspectives_dict[str(pm.perspective_id)] = pm.value
                row['perspectives'] = dict(perspectives_dict)
                table.append(row)

            # Adicionar valores possíveis de perspetiva (igual ao GetAllFilledValues)
            # Obter todos os membros de perspetiva deste projeto (todas as versões)
            all_project_versions = Project.objects.filter(
                models.Q(id=original_project.id) | 
                models.Q(original_project=original_project)
            ).values_list('id', flat=True)
            perspective_members = PerspectiveMember.objects.filter(
                member__project_id__in=all_project_versions
            ).select_related('perspective')
            perspective_values_dict = {}
            for member in perspective_members:
                if member.perspective_id not in perspective_values_dict:
                    perspective_values_dict[member.perspective_id] = set()
                perspective_values_dict[member.perspective_id].add(member.value)
            # Converter sets em listas
            for perspective_id in perspective_values_dict:
                perspective_values_dict[perspective_id] = list(perspective_values_dict[perspective_id])
            return Response({
                'labels': all_labels,
                'rows': table,
                'perspective_values': perspective_values_dict
            })
        except DatabaseError:
            return Response(
                {"detail": "Sorry, we couldn't load the label table right now. Please try again in a few moments."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DiscrepancyCommentListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, discrepancy_id):
        from django.db import DatabaseError
        try:
            comments = DiscrepancyComment.objects.filter(discrepancy_id=discrepancy_id)
            serializer = DiscrepancyCommentSerializer(comments, many=True)
            return Response(serializer.data)
        except DatabaseError:
            return Response(
                {"detail": "Sorry, we couldn't load the comments right now. Please try again in a few moments."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, discrepancy_id):
        data = request.data.copy()
        data["discrepancy"] = discrepancy_id
        data["user"] = request.user.id
        serializer = DiscrepancyCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

