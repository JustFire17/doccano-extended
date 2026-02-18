from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import Group, Permission
from django.db import IntegrityError, DatabaseError

from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from projects.permissions import IsProjectAdmin
from .serializers import GroupSerializer, PermissionSerializer


class Groups(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("name",)

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except DatabaseError:
            return Response(
                {"detail": "Sorry, we couldn't load the groups right now. Please try again in a few moments."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GroupCreation(generics.CreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            if 'name' in e.detail:
                return Response(
                    {"detail": "A group with this name already exists. Please choose a different name."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            raise e
        except DatabaseError:
            return Response(
                {"detail": "Sorry, we couldn't create the group right now. Please try again in a few moments."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GroupDeletion(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    def delete(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        except DatabaseError:
            return Response(
                {"detail": "Sorry, we couldn't delete the group right now. Please try again in a few moments."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GroupDetail(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            if 'name' in e.detail:
                return Response(
                    {"detail": "A group with this name already exists. Please choose a different name."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            raise e
        except DatabaseError:
            return Response(
                {"detail": "Sorry, we couldn't update the group right now. Please try again in a few moments."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PermissionList(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]