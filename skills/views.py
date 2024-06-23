from django.views.generic import ListView, DetailView
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

    # model = Skill
    # template_name = "skills/skill_detail.html"
    # context_object_name = "skill"
    pass
