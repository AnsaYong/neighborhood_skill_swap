from django.urls import path

from .views import SkillListView, SkillDetailView, SkillUpdateView, SkillDeleteView

urlpatterns = [
    path("<int:pk>/delete/", SkillDeleteView.as_view(), name="skill_delete"),
    path("<int:pk>/edit/", SkillUpdateView.as_view(), name="skill_edit"),
    path("<int:pk>/", SkillDetailView.as_view(), name="skill_detail"),
    path("", SkillListView.as_view(), name="skill_list"),
]
