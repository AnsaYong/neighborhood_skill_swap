from django.urls import path

from .views_skills import (
    SkillReviewCreateView,
    SkillListView,
    SkillDetailView,
    SkillUpdateView,
    SkillDeleteView,
    SkillCreateView,
)
from .views_deals import (
    SkillDealCreateView,
    SkillDealAcceptView,
    SkillDealUpdateView,
    SkillDealListView,
    SkillDealDetailView,
    SkillDealCompleteView,
    ProvidedDealsView,
    RequestedDealsView,
)
from .views_messages import MessageListView

urlpatterns = [
    # Skill urls
    path("review/<int:pk>/", SkillReviewCreateView.as_view(), name="skill_review"),
    path("<int:pk>/delete/", SkillDeleteView.as_view(), name="skill_delete"),
    path("<int:pk>/edit/", SkillUpdateView.as_view(), name="skill_edit"),
    path("<int:pk>/", SkillDetailView.as_view(), name="skill_detail"),
    path("new/", SkillCreateView.as_view(), name="skill_new"),
    path("new/wanted/", SkillCreateView.as_view(), name="skill_new_wanted"),
    path("search/", SkillListView.as_view(), name="skill_search"),
    path("all/", SkillListView.as_view(), name="all"),
    path("", SkillListView.as_view(), name="skill_list"),
    path("<str:skill_type>", SkillListView.as_view(), name="skills"),
    path(
        "categories/<str:category>/", SkillListView.as_view(), name="skill_by_category"
    ),
    # Skill deal urls
    path(
        "deals/new/<int:skill_pk>", SkillDealCreateView.as_view(), name="skill_deal_new"
    ),
    path(
        "deals/accept/<int:deal_pk>",
        SkillDealAcceptView.as_view(),
        name="skill_deal_accept",
    ),
    path("deals/", SkillDealListView.as_view(), name="skill_deal_list"),
    path("deals/provided/", ProvidedDealsView.as_view(), name="provided_deals"),
    path("deals/requested/", RequestedDealsView.as_view(), name="requested_deals"),
    path("deals/<int:pk>/", SkillDealDetailView.as_view(), name="skill_deal_detail"),
    path("deals/<int:pk>/edit/", SkillDealUpdateView.as_view(), name="skill_deal_edit"),
    path(
        "deals/<int:deal_pk>/complete/",
        SkillDealCompleteView.as_view(),
        name="skill_deal_complete",
    ),
    # Message urls
    path("messages/", MessageListView.as_view(), name="message_list"),
]
