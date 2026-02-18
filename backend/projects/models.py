import abc
import uuid
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager
from polymorphic.models import PolymorphicModel
from copy import copy

from roles.models import Role


class ProjectType(models.TextChoices):
    DOCUMENT_CLASSIFICATION = "DocumentClassification"
    SEQUENCE_LABELING = "SequenceLabeling"
    SEQ2SEQ = "Seq2seq"
    INTENT_DETECTION_AND_SLOT_FILLING = "IntentDetectionAndSlotFilling"
    SPEECH2TEXT = "Speech2text"
    IMAGE_CLASSIFICATION = "ImageClassification"
    BOUNDING_BOX = "BoundingBox"
    SEGMENTATION = "Segmentation"
    IMAGE_CAPTIONING = "ImageCaptioning"


class Project(PolymorphicModel):
    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    guideline = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    project_type = models.CharField(max_length=30, choices=ProjectType.choices)
    random_order = models.BooleanField(default=False)
    collaborative_annotation = models.BooleanField(default=False)
    single_class_classification = models.BooleanField(default=False)
    allow_member_to_create_label_type = models.BooleanField(default=False)

    discrepancy_active = models.BooleanField()
    discrepancy_percentage = models.FloatField(default=0)

    perspective_associated = models.ForeignKey("PerspectiveProject",on_delete=models.SET_NULL,null=True,blank=True,related_name="projects")

    closed = models.BooleanField(default=False)
    
    # New fields for versioning
    version = models.IntegerField(default=1)
    original_project = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='versions')
    is_current_version = models.BooleanField(default=True)

    def add_admin(self):
        admin_role = Role.objects.get(name=settings.ROLE_PROJECT_ADMIN)
        Member.objects.create(
            project=self,
            user=self.created_by,
            role=admin_role,
        )

    @property
    @abc.abstractmethod
    def is_text_project(self) -> bool:
        return False

    def clone(self) -> "Project":
        """Clone the project.
        See https://docs.djangoproject.com/en/4.2/topics/db/queries/#copying-model-instances

        Returns:
            The cloned project.
        """
        project = Project.objects.get(pk=self.pk)
        project.pk = None
        project.id = None
        # Reset versioning fields
        project.version = 1
        project.original_project = None
        project.is_current_version = True
        project._state.adding = True
        project.save()

        def bulk_clone(queryset: models.QuerySet, field_initializers: Optional[Dict[Any, Any]] = None):
            """Clone the queryset.

            Args:
                queryset: The queryset to clone.
                field_initializers: The field initializers.
            """
            if field_initializers is None:
                field_initializers = {}
            items = []
            for item in queryset:
                item.id = None
                item.pk = None
                for field, value_or_callable in field_initializers.items():
                    if callable(value_or_callable):
                        value_or_callable = value_or_callable()
                    setattr(item, field, value_or_callable)
                item.project = project
                item._state.adding = True
                items.append(item)
            queryset.model.objects.bulk_create(items)

        bulk_clone(self.role_mappings.all())
        bulk_clone(self.tags.all())

        # clone examples with original_example reference
        original_examples = list(self.examples.all())
        cloned_examples = []
        for original_example in original_examples:
            # Create a proper copy
            cloned_example = copy(original_example)
            cloned_example.id = None
            cloned_example.pk = None
            cloned_example.uuid = uuid.uuid4()
            cloned_example.project = project
            # Set original_example to the original if not already set, otherwise keep the existing reference
            if not original_example.original_example:
                cloned_example.original_example = original_example
            else:
                cloned_example.original_example = original_example.original_example
            cloned_example._state.adding = True
            cloned_examples.append(cloned_example)
        
        # Bulk create the cloned examples
        from examples.models import Example
        Example.objects.bulk_create(cloned_examples)

        # clone label types
        bulk_clone(self.categorytype_set.all())
        bulk_clone(self.spantype_set.all())
        bulk_clone(self.relationtype_set.all())

        return project

    def create_new_version(self) -> "Project":
        """Create a new version of the project.
        
        Returns:
            The new version of the project.
        """
        # Get the original project (either self or the original_project)
        original = self.original_project or self
        
        # Create a new project instance (not using clone to avoid copying examples)
        new_version = Project.objects.get(pk=self.pk)
        new_version.pk = None
        new_version.id = None
        new_version._state.adding = True
        
        # Get the highest version number from all versions of the original project
        max_version = Project.objects.filter(
            models.Q(id=original.id) | models.Q(original_project=original)
        ).aggregate(models.Max('version'))['version__max']
        
        # Set the new version number and relationships
        new_version.version = max_version + 1 if max_version is not None else 1
        new_version.original_project = original
        new_version.is_current_version = True
        new_version.closed = False
        new_version.save()
        
        # Mark all other versions as not current
        original.versions.exclude(id=new_version.id).update(is_current_version=False)
        
        # Copy role mappings to new version
        for member in self.role_mappings.all():
            Member.objects.create(
                user=member.user,
                project=new_version,
                role=member.role
            )
        
        # Copy tags to new version
        for tag in self.tags.all():
            Tag.objects.create(
                text=tag.text,
                project=new_version
            )
        
        # Copy label types to new version
        for category_type in self.categorytype_set.all():
            category_type.pk = None
            category_type.id = None
            category_type.project = new_version
            category_type._state.adding = True
            category_type.save()
            
        for span_type in self.spantype_set.all():
            span_type.pk = None
            span_type.id = None
            span_type.project = new_version
            span_type._state.adding = True
            span_type.save()
            
        for relation_type in self.relationtype_set.all():
            relation_type.pk = None
            relation_type.id = None
            relation_type.project = new_version
            relation_type._state.adding = True
            relation_type.save()
        
        # Copy rules to new version
        for rule in self.rules.all():
            Rule.objects.create(
                project=new_version,
                name=rule.name,
                description=rule.description,
                version=rule.version  # Maintain the original version of the rule
            )
        

        # IMPORTANT: Examples are NOT copied - they remain associated with the original project
        # This way, all versions share the same examples with the same IDs
        # Copy perspective members from the current project to the new version
        if self.perspective_associated:
            # Get all members from the current project
            current_members = self.role_mappings.all()
            
            # Get all perspectives from the associated perspective project
            perspectives = Perspective.objects.filter(perspective_project=self.perspective_associated)
            
            # For each member in the current project
            for current_member in current_members:
                # Find the corresponding member in the new version
                new_member = new_version.role_mappings.filter(user=current_member.user).first()
                
                if new_member:
                    # Copy all perspective values for this member
                    for perspective in perspectives:
                        # Get the current value if it exists
                        current_value = PerspectiveMember.objects.filter(
                            member=current_member,
                            perspective=perspective
                        ).first()
                        
                        if current_value:
                            # Create the same value in the new version
                            PerspectiveMember.objects.create(
                                member=new_member,
                                perspective=perspective,
                                value=current_value.value
                            )
        
        return new_version

    def __str__(self):
        return f"{self.name} (v{self.version})"


class TextClassificationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class SequenceLabelingProject(Project):
    allow_overlapping = models.BooleanField(default=False)
    grapheme_mode = models.BooleanField(default=False)
    use_relation = models.BooleanField(default=False)

    @property
    def is_text_project(self) -> bool:
        return True


class Seq2seqProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class IntentDetectionAndSlotFillingProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class Speech2textProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class ImageClassificationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class BoundingBoxProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class SegmentationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class ImageCaptioningProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class Tag(models.Model):
    text = models.TextField()
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="tags")

    def __str__(self):
        return self.text


class MemberManager(Manager):
    def can_update(self, project: int, member_id: int, new_role: str) -> bool:
        """The project needs at least 1 admin.

        Args:
            project: The project id.
            member_id: The member id.
            new_role: The new role name.

        Returns:
            Whether the mapping can be updated or not.
        """
        queryset = self.filter(project=project, role__name=settings.ROLE_PROJECT_ADMIN)
        if queryset.count() > 1:
            return True
        else:
            admin = queryset.first()
            # we can change the role except for the only admin.
            return admin.id != member_id or new_role == settings.ROLE_PROJECT_ADMIN

    def has_role(self, project_id: int, user: User, role_name: str):
        return self.filter(project=project_id, user=user, role__name=role_name).exists()


class Member(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="role_mappings")
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="role_mappings")
    role = models.ForeignKey(to=Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MemberManager()

    def clean(self):
        members = self.__class__.objects.exclude(id=self.id)
        if members.filter(user=self.user, project=self.project).exists():
            message = "This user is already assigned to a role in this project."
            raise ValidationError(message)

    def is_admin(self):
        return self.role.name == settings.ROLE_PROJECT_ADMIN

    @property
    def username(self):
        return self.user.username

    class Meta:
        unique_together = ("user", "project")

class RuleVote(models.Model):
    rule = models.ForeignKey("Rule", on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_upvote = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("rule", "user")

class Rule(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="rules")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    voting_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)
    voting_end_date = models.DateField(null=True, blank=True)
    voting_end_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = [('project', 'name'), ('project', 'description')]

    def clean(self):
        # Validate name is not empty
        if not self.name.strip():
            raise ValidationError("Rule name cannot be empty")
        
        # Validate description is not empty
        if not self.description.strip():
            raise ValidationError("Rule description cannot be empty")
        
        # Check for duplicate name in the same project
        if Rule.objects.filter(project=self.project, name=self.name).exclude(id=self.id).exists():
            raise ValidationError("A rule with this name already exists in this project")
        
        # Check for duplicate description in the same project
        if Rule.objects.filter(project=self.project, description=self.description).exclude(id=self.id).exists():
            raise ValidationError("A rule with this description already exists in this project")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def upvotes_count(self):
        return self.votes.filter(is_upvote=True).count()

    @property
    def downvotes_count(self):
        return self.votes.filter(is_upvote=False).count()

    @property
    def vote_percentage(self):
        total_votes = self.upvotes_count + self.downvotes_count
        if total_votes == 0:
            return 0
        return (self.upvotes_count / total_votes) * 100

    def get_user_vote(self, user):
        """Get the current user's vote on this rule.

        Args:
            user: The user to check the vote for.

        Returns:
            'upvote' if the user upvoted, 'downvote' if downvoted, None if no vote.
        """
        vote = self.votes.filter(user=user).first()
        if not vote:
            return None
        return 'upvote' if vote.is_upvote else 'downvote'

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class PerspectiveProject(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_perspective_projects"
    )

    def __str__(self):
        return self.name


class Perspective(models.Model):
    perspective_project = models.ForeignKey(PerspectiveProject, on_delete=models.CASCADE, related_name="perspectives", null=True)
    TYPE_CHOICES = [("number", "Number"), ("string", "String"), ("yes/no", "Yes/No"), ("options", "Options")]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    options = models.CharField(max_length=1024, blank=True, default="")

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    


class PerspectiveMember(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="perspective_values")
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name="values")
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.member.user.username} → {self.perspective.name}: {self.value}"\

class ManualDiscrepancy(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="manual_discrepancies")
    example = models.ForeignKey("examples.Example", on_delete=models.CASCADE, related_name="manual_discrepancies")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=[("unsolved", "Unsolved"), ("solved", "Solved")], default="unsolved")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DiscrepancyLabelStat(models.Model):
    discrepancy = models.ForeignKey(ManualDiscrepancy, on_delete=models.CASCADE, related_name="label_stats")
    label_text = models.CharField(max_length=255)
    vote_count = models.IntegerField()
    percentage = models.FloatField()  # exemplo: 30.0 representa 30%

# Discussion models for the discussion chat feature
class Discussion(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed")
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="discussions")
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_discussions")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project_version = models.IntegerField(help_text="Version of the project when the discussion was created")

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.project_version = self.project.version
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()}) - {self.project.name}"
    
    @property
    def participants(self):
        """Return a list of unique users who have participated in the discussion"""
        return User.objects.filter(messages__discussion=self).distinct()

class DiscussionMessage(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"

class DiscrepancyComment(models.Model):
    discrepancy = models.ForeignKey(ManualDiscrepancy, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discrepancy_comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} on {self.discrepancy.id}: {self.content[:30]}"