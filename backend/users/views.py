from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .serializers import CustomRegisterSerializer
from projects.models import Member

from .serializers import UserSerializer, UserUpdateSerializer
from projects.permissions import IsProjectAdmin


class Me(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class Users(generics.ListAPIView):     
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("username",)


class UserCreation(generics.CreateAPIView):
    serializer_class = CustomRegisterSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer, request)
        headers = self.get_success_headers(serializer.data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, request):
        user = serializer.save(request=request)
        return user


class UserDeletion(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    def delete(self, request, user_id):
        try:
            if(request.user.id == user_id):
                return Response({"error": "Super-user can't delete oneself"}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(id=user_id)
            
            # Check if user is associated with any projects
            if Member.objects.filter(user=user).exists():
                # Instead of deleting, mark as inactive
                user.is_active = False
                user.save()
                return Response({"message": "User has been deactivated because they are associated with projects"}, status=status.HTTP_200_OK)
            
            # If no project associations, proceed with deletion
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]
    lookup_field = 'id'
    lookup_url_kwarg = 'user_id'


class UserUpdate(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]
    

class SetPassword(APIView):
    permission_classes = [IsAuthenticated & IsAdminUser]

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")

        if not password1 or not password2:
            return Response({"error": "Both password fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if password1 != password2:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password1, user)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(password1)  # Encripta a nova password
        user.save()

        return Response({"message": "Password updated successfully!"}, status=status.HTTP_200_OK)