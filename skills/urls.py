from django.urls import path

from .views import (
    SkillReviewCreateView,
    SkillListView,
    SkillDetailView,
    SkillUpdateView,
    SkillDeleteView,
    SkillCreateView,
    SkillDealCreateView,
    SkillDealAcceptView,
    SkillDealUpdateView,
    SkillDealListView,
    SkillDealDetailView,
    SkillDealCompleteView,
)

urlpatterns = [
    path("review/<int:pk>/", SkillReviewCreateView.as_view(), name="skill_review"),
    path("<int:pk>/delete/", SkillDeleteView.as_view(), name="skill_delete"),
    path("<int:pk>/edit/", SkillUpdateView.as_view(), name="skill_edit"),
    path("<int:pk>/", SkillDetailView.as_view(), name="skill_detail"),
    path("new/", SkillCreateView.as_view(), name="skill_new"),
    path("new/wanted/", SkillCreateView.as_view(), name="skill_new_wanted"),
    path("search/", SkillListView.as_view(), name="skill_search"),
    path("all", SkillListView.as_view(), name="all"),
    path("", SkillListView.as_view(), name="skill_list"),
    path(
        "categories/<str:category>/", SkillListView.as_view(), name="skill_by_category"
    ),
    path(
        "deals/new/<int:skill_pk>", SkillDealCreateView.as_view(), name="skill_deal_new"
    ),
    path(
        "deals/accept/<int:deal_pk>",
        SkillDealAcceptView.as_view(),
        name="skill_deal_accept",
    ),
    path("deals/", SkillDealListView.as_view(), name="skill_deal_list"),
    path("deals/<int:pk>/", SkillDealDetailView.as_view(), name="skill_deal_detail"),
    path("deals/<int:pk>/edit/", SkillDealUpdateView.as_view(), name="skill_deal_edit"),
    path(
        "deals/<int:deal_pk>/complete/",
        SkillDealCompleteView.as_view(),
        name="skill_deal_complete",
    ),
]
