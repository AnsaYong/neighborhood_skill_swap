from django.urls import path

from .views import SkillListView, SkillDetailView

urlpatterns = [
    path("", SkillListView.as_view(), name="skill_list"),
    path("skils/<int:pk>/", SkillDetailView.as_view(), name="skill_detail"),
]
