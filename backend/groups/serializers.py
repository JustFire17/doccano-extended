from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError
from rest_framework import serializers

class PermissionSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = "__all__"

    def get_description(self, obj):
        return f"{obj.content_type.app_label} | {obj.content_type.model} | {obj.name}"
    


class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    permission_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Group
        fields = "__all__"

    def validate(self, data):
        permission_ids = data.get('permission_ids', [])
        if not permission_ids:
            raise serializers.ValidationError({"detail": "A group must have at least one permission."})

        # Validar nome duplicado
        name = data.get('name')
        if name:
            query = Group.objects.filter(name=name)
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError({"name": ["A group with this name already exists. Please choose a different name."]})
        
        return data

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        try:
            group = super().create(validated_data)
            group.permissions.set(permission_ids)
            return group
        except IntegrityError:
            raise serializers.ValidationError({"name": ["A group with this name already exists. Please choose a different name."]})

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        try:
            group = super().update(instance, validated_data)
            group.permissions.set(permission_ids)
            return group
        except IntegrityError:
            raise serializers.ValidationError({"name": ["A group with this name already exists. Please choose a different name."]})