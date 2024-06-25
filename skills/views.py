from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    CreateView,
)
from django.urls import reverse_lazy
from .models import Skill


# Create your views here.
class SkillListView(ListView):
    """A view to display a list of skills.

    Attributes:
        model: A model to represent the skills.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    template_name = "skills/skill_list.html"
    context_object_name = "skills"


class SkillDetailView(DetailView):
    """A view to display the detail of a skill.

    Attributes:
        model: A model to represent the skills.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    template_name = "skills/skill_detail.html"
    context_object_name = "skill"


class SkillUpdateView(UpdateView):
    """A view to update the detail of a skill.

    Attributes:
        model: A model to represent the skills.
        fields: A tuple to represent the fields that can be edited.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    fields = ("name", "description")
    template_name = "skills/skill_edit.html"
    context_object_name = "skill"


class SkillDeleteView(DeleteView):
    """A view to delete the specified skill.

    Attributes:
        model: A model to represent the skills.
        template_name: A string to represent the template file.
        success_url: A string to represent the URL to redirect to after deleting the skill.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    template_name = "skills/skill_delete.html"
    success_url = reverse_lazy("skill_list")
    context_object_name = "skill"


class SkillCreateView(CreateView):
    """A view to create a new skill.

    Attributes:
        model: A model to represent the skills.
        fields: A tuple to represent the fields that can be edited.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    fields = (
        "name",
        "category",
        "Level",
        "description",
        "owner",
    )
    template_name = "skills/skill_create.html"
    context_object_name = "skill"
