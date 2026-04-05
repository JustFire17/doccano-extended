from django.urls import include, path

from .views import Me, UserCreation, Users, UserDeletion, UserDetail, UserUpdate, SetPassword

urlpatterns = [
    path(route="me", view=Me.as_view(), name="me"),
    path(route="users", view=Users.as_view(), name="user_list"),
    path(route="users/create", view=UserCreation.as_view(), name="user_create"),
    path(route="users/delete/<int:user_id>", view=UserDeletion.as_view(), name="user_delete"),
    path(route="users/<int:user_id>", view=UserDetail.as_view(), name="user_detail"),
    path(route="users/update/<int:pk>", view=UserUpdate.as_view(), name="user_update"),
    path(route="users/<int:user_id>/set_password/", view=SetPassword.as_view(), name="set_password"),
    path("auth/", include("dj_rest_auth.urls")),
]