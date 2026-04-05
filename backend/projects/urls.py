from django.urls import path

from .views.member import MemberDetail, MemberList, MyRole

from .views.project import (
    CloneProject, 
    FillPerspectives, 
    GetFilledPerspectives,
    LabelStatsView, 
    ProjectDetail, 
    ProjectList,
    DiscrepancyAnalysisView, 
    AllPerspectivesView,
    GetAllFilledValues,
    GetUsersWithValue,
    AnnotationsByUserView,
    ManualDiscrepancyListCreate,
    CreatePerspectiveWithItems,
    AssociatePerspectiveView,
    PerspectiveList,
    AnnotatorReportView,
    AnnotationStatisticsView,
    AllVersionsStatisticsView,
    CloseProject,
    ReopenProject,
    RuleListCreate,
    RuleDetail,
    RuleVoteView,
    CloseRuleVote,
    ReopenRuleVote,
    ProjectVersionsList,
    DeletePerspectiveTotal,
    AnnotationLabelTableView,
    DiscrepancyCommentListCreate,
)

from .views.tag import TagDetail, TagList

from .views.discussion import (
    DiscussionList,
    DiscussionDetail,
    DiscussionMessageList,
    DiscussionMessageDetail
)

urlpatterns = [
    path(route="projects", view=ProjectList.as_view(), name="project_list"),
    path(route="projects/<int:project_id>", view=ProjectDetail.as_view(), name="project_detail"),
    path(route="projects/<int:project_id>/my-role", view=MyRole.as_view(), name="my_role"),
    path(route="projects/<int:project_id>/tags", view=TagList.as_view(), name="tag_list"),
    path(route="projects/<int:project_id>/tags/<int:tag_id>", view=TagDetail.as_view(), name="tag_detail"),
    path(route="projects/<int:project_id>/members", view=MemberList.as_view(), name="member_list"),
    path(route="projects/<int:project_id>/clone", view=CloneProject.as_view(), name="clone_project"),
    path(route="projects/<int:project_id>/members/<int:member_id>", view=MemberDetail.as_view(), name="member_detail"),

    ## Perspectives
    path(route="projects/<int:project_id>/perspectives", view=PerspectiveList.as_view(), name="perspective_list"),
    path(route="projects/<int:project_id>/perspectives/<int:perspective_id>", view=PerspectiveList.as_view(), name="perspective_detail"),
    path(route="projects/<int:project_id>/perspectives/create-with-items", view=CreatePerspectiveWithItems.as_view(), name="perspective_create_with_items"),
    path("projects/<int:project_id>/associate-perspective", AssociatePerspectiveView.as_view(), name="associate_perspective"),
    path(route="projects/<int:project_id>/perspectives/fill", view=FillPerspectives.as_view(), name="perspective_fill"),
    path("projects/<int:project_id>/perspectives/fill/values", GetFilledPerspectives.as_view(), name="get_filled_perspectives"),
    path("projects/<int:project_id>/perspectives/fill/all-values", GetAllFilledValues.as_view(), name="get_all_filled_values"),
    path("projects/<int:project_id>/perspectives/fill/users-with-value", GetUsersWithValue.as_view(), name="get_users_with_value"),
    path("projects/<int:project_id>/AllPerspectives", AllPerspectivesView.as_view(), name="all_perspectives"),
    path(route="projects/<int:project_id>/perspectives/<int:perspective_id>/delete-total", view=DeletePerspectiveTotal.as_view(), name="perspective-delete-total"),

    ## Reports
    path(route="projects/<int:project_id>/reports/annotators", view=AnnotatorReportView.as_view(), name="annotator_report"),
    path(route="projects/<int:project_id>/annotation-statistics", view=AnnotationStatisticsView.as_view(), name='annotation-statistics'),
    path(route="projects/<int:project_id>/all-versions-statistics", view=AllVersionsStatisticsView.as_view(), name='all-versions-statistics'),
    path('projects/<int:project_id>/annotation-label-table/', AnnotationLabelTableView.as_view(), name='annotation-label-table'),
    ## Discrepancy
    path(route="projects/<int:project_id>/discrepancies", view=DiscrepancyAnalysisView.as_view(), name='discrepancy-analysis'),
    path(route="projects/<int:project_id>/annotations-by-user", view=AnnotationsByUserView.as_view(), name='annotations-by-user'),
    path(route="projects/<int:project_id>/discrepancies/create", view=ManualDiscrepancyListCreate.as_view(), name='manual-discrepancy-create'),
    path(route="projects/<int:project_id>/examples/<int:example_id>/label-stats", view=LabelStatsView.as_view(), name="label_stats"),
    path(route="projects/<int:project_id>/manual-discrepancies", view=ManualDiscrepancyListCreate.as_view(), name='manual-discrepancy-list'),
    path(
        route="discrepancies/<int:discrepancy_id>/comments",
        view=DiscrepancyCommentListCreate.as_view(),
        name="discrepancy-comment-list-create"
    ),
    
    ## Discussions
    path(route="projects/<int:project_id>/discussions", view=DiscussionList.as_view(), name="discussion_list"),
    path(route="projects/<int:project_id>/discussions/<int:discussion_id>", view=DiscussionDetail.as_view(), name="discussion_detail"),
    path(route="projects/<int:project_id>/discussions/<int:discussion_id>/messages", view=DiscussionMessageList.as_view(), name="discussion_message_list"),
    path(route="projects/<int:project_id>/discussions/<int:discussion_id>/messages/<int:message_id>", view=DiscussionMessageDetail.as_view(), name="discussion_message_detail"),
    
    #Rules
    path(route="projects/<int:project_id>/close", view=CloseProject.as_view(), name="close_project"),
    path(route="projects/<int:project_id>/reopen", view=ReopenProject.as_view(), name="reopen_project"),
    path(route="projects/<int:project_id>/rules", view=RuleListCreate.as_view(), name="rule_list_create"),
    path(route="projects/<int:project_id>/rules/<int:rule_id>", view=RuleDetail.as_view(), name="rule_detail"),
    path(route="projects/<int:project_id>/rules/<int:rule_id>/vote/", view=RuleVoteView.as_view(), name="rule-vote"),
    path(route="projects/<int:project_id>/rules/<int:rule_id>/close-vote/", view=CloseRuleVote.as_view(), name="close-rule-vote"),
    path(route="projects/<int:project_id>/rules/<int:rule_id>/reopen-vote/", view=ReopenRuleVote.as_view(), name="reopen-rule-vote"),
    path(route="projects/<int:project_id>/versions", view=ProjectVersionsList.as_view(), name="project_versions_list"),
]
