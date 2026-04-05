from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from rest_framework.exceptions import ValidationError

from .models import (
    BoundingBoxProject,
    ImageCaptioningProject,
    ImageClassificationProject,
    IntentDetectionAndSlotFillingProject,
    Member,
    Project,
    SegmentationProject,
    Seq2seqProject,
    SequenceLabelingProject,
    Speech2textProject,
    Tag,
    TextClassificationProject,
    Perspective,
    PerspectiveMember,
    ManualDiscrepancy,
    DiscrepancyLabelStat,
    PerspectiveProject,
    Discussion,
    DiscussionMessage,
    Rule,
    DiscrepancyComment
)


class MemberSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    rolename = serializers.SerializerMethodField()

    @classmethod
    def get_username(cls, instance):
        user = instance.user
        return user.username if user else None

    @classmethod
    def get_rolename(cls, instance):
        role = instance.role
        return role.name if role else None

    class Meta:
        model = Member
        fields = ("id", "user", "role", "username", "rolename")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "project",
            "text",
        )
        read_only_fields = ("id", "project")


class ProjectSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = serializers.SerializerMethodField()
    discrepancy_active = serializers.BooleanField()
    perspective_associated = serializers.PrimaryKeyRelatedField(
        queryset=PerspectiveProject.objects.all(),
        required=False,
        allow_null=True
    )

    @classmethod
    def get_author(cls, instance):
        if instance.created_by:
            return instance.created_by.username
        return ""

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "guideline",
            "project_type",
            "created_at",
            "updated_at",
            "random_order",
            "author",
            "collaborative_annotation",
            "single_class_classification",
            "allow_member_to_create_label_type",
            "is_text_project",
            "tags",
            "discrepancy_active",
            "discrepancy_percentage",
            "perspective_associated",
            "closed",
            "version",
            "original_project",
            "is_current_version"
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "author",
            "is_text_project",
            "version",
            "original_project",
            "is_current_version"
        )

    def create(self, validated_data):
        tags = TagSerializer(data=validated_data.pop("tags", []), many=True)
        project = self.Meta.model.objects.create(**validated_data)
        tags.is_valid()
        tags.save(project=project)
        return project

    def update(self, instance, validated_data):
        validated_data.pop("tags", None)
        return super().update(instance, validated_data)




class TextClassificationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = TextClassificationProject


class SequenceLabelingProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = SequenceLabelingProject
        fields = ProjectSerializer.Meta.fields + ["allow_overlapping", "grapheme_mode", "use_relation"]


class Seq2seqProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = Seq2seqProject


class IntentDetectionAndSlotFillingProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = IntentDetectionAndSlotFillingProject


class Speech2textProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = Speech2textProject


class ImageClassificationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = ImageClassificationProject


class BoundingBoxProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = BoundingBoxProject


class SegmentationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = SegmentationProject


class ImageCaptioningProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = ImageCaptioningProject


class ProjectPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Project: ProjectSerializer,
        **{cls.Meta.model: cls for cls in ProjectSerializer.__subclasses__()},
    }

class RuleSerializer(serializers.ModelSerializer):
    upvotes_count = serializers.IntegerField(read_only=True)
    downvotes_count = serializers.IntegerField(read_only=True)
    vote_percentage = serializers.FloatField(read_only=True)
    user_vote = serializers.SerializerMethodField()

    class Meta:
        model = Rule
        fields = ['id', 'project', 'name', 'description', 'created_at', 'updated_at', 'upvotes_count', 'downvotes_count', 'vote_percentage', 'user_vote', 'voting_closed', 'version', 'voting_end_date', 'voting_end_time']
        read_only_fields = ['id', 'created_at', 'updated_at', 'upvotes_count', 'downvotes_count', 'vote_percentage', 'user_vote']
        extra_kwargs = {
            'name': {'error_messages': {'blank': 'Rule name cannot be empty'}},
            'description': {'error_messages': {'blank': 'Rule description cannot be empty'}}
        }

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        return obj.get_user_vote(request.user)

    def validate(self, data):
        try:
            # Create a temporary instance to run model validation
            rule = Rule(**data)
            rule.full_clean()
        except ValidationError as e:
            # Convert Django ValidationError to DRF ValidationError with proper error format
            error_dict = {}
            for field, errors in e.error_dict.items():
                error_dict[field] = [str(error) for error in errors]
            raise serializers.ValidationError(error_dict)
        return data

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Rule name cannot be empty")
        return value

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Rule description cannot be empty")
        return value


class PerspectiveSerializer(serializers.ModelSerializer):
    perspective_project = serializers.PrimaryKeyRelatedField(read_only=True)
    values = serializers.SerializerMethodField()

    class Meta:
        model = Perspective
        fields = ['id' , 'perspective_project', 'name', 'type', 'options', 'values']
        read_only_fields = ['id', 'project']

    def get_values(self, obj):
        perspective_members = obj.values.all()
        return [member.value for member in perspective_members]

    def validate(self, data):
        project = self.context['request'].parser_context['kwargs']['project_id']
        name = data['name']
        if Perspective.objects.filter(name=name, project_id=project).exists():
            raise ValidationError({'name': 'An item with this name already exists in the perspective.'})
        return data

    def create(self, validated_data):
        return super().create(validated_data)


class PerspectiveMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveMember
        fields = ["id", "member", "perspective", "value"]
        
        
class PerspectiveValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveMember
        fields = ["perspective", "value"]
        
        
class DiscrepancyLabelStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscrepancyLabelStat
        fields = ["label_text", "vote_count", "percentage"]

class ManualDiscrepancySerializer(serializers.ModelSerializer):
    label_stats = DiscrepancyLabelStatSerializer(many=True, read_only=True)
    reported_by_username = serializers.SerializerMethodField()

    class Meta:
        model = ManualDiscrepancy
        fields = [
            "id",
            "project",
            "example",
            "reported_by",
            "reported_by_username",
            "description",
            "status",
            "created_at",
            "updated_at",
            "label_stats"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "reported_by_username", "label_stats"]

    def get_reported_by_username(self, obj):
        return obj.reported_by.username if obj.reported_by else None

class DiscussionMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionMessage
        fields = [
            "id",
            "discussion",
            "sender",
            "sender_username",
            "content",
            "created_at"
        ]
        read_only_fields = ["id", "created_at", "sender_username"]
    
    def get_sender_username(self, obj):
        return obj.sender.username if obj.sender else None

class DiscussionSerializer(serializers.ModelSerializer):
    created_by_username = serializers.SerializerMethodField()
    messages = DiscussionMessageSerializer(many=True, read_only=True)
    participants_count = serializers.SerializerMethodField()
    annotators = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = [
            "id",
            "project",
            "name",
            "created_by",
            "created_by_username",
            "status",
            "created_at",
            "updated_at",
            "messages",
            "participants_count",
            "annotators",
            "project_version"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by_username", "participants_count", "annotators", "project_version"]
    
    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else None
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    
    def get_annotators(self, obj):
        """Return list of project annotators with their usernames"""
        from django.conf import settings
        from projects.models import Member
        
        # Get the original project to ensure we get all annotators across versions
        original_project = obj.project.original_project or obj.project
        
        # Get all members of the project (excluding admins and those with only read access)
        project_members = Member.objects.filter(
            project=original_project,
            role__name__in=[settings.ROLE_ANNOTATOR, settings.ROLE_ANNOTATION_APPROVER]
        ).select_related('user', 'role')
        
        annotators = []
        for member in project_members:
            if member.user:
                annotators.append({
                    'id': member.user.id,
                    'username': member.user.username,
                    'role': member.role.name
                })
        
        return annotators

class DiscrepancyCommentSerializer(serializers.ModelSerializer):
    user_username = serializers.SerializerMethodField()

    class Meta:
        model = DiscrepancyComment
        fields = [
            "id",
            "discrepancy",
            "user",
            "user_username",
            "content",
            "created_at"
        ]
        read_only_fields = ["id", "created_at", "user_username"]

    def get_user_username(self, obj):
        return obj.user.username if obj.user else None