from django.urls import path

from .views import (
    SkillListView,
    SkillDetailView,
    SkillUpdateView,
    SkillDeleteView,
    SkillCreateView,
)

urlpatterns = [
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
]
