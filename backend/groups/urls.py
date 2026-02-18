from django.urls import path
from .views import Groups, GroupCreation, GroupDeletion, GroupDetail, PermissionList

urlpatterns = [
    path('groups', Groups.as_view(), name='group-list'),
    path("groups/create", GroupCreation.as_view(), name="group_create"),
    path("groups/update/<int:pk>/", GroupDetail.as_view(), name="group_update"),
    path("groups/delete/<int:group_id>/", GroupDeletion.as_view(), name="group_delete"),
    path('groups/permissions/', PermissionList.as_view(), name='permission-list'),
]