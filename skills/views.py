from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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
class SkillListView(LoginRequiredMixin, ListView):
    """A view to display a list of the logged in user's skills,
    optionally filtered by category.

    LoginRequiredMixin: A mixin to require the user to be logged in.

    Attributes:
        model: A model to represent the skills.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    template_name = "skills/skill_list_user.html"
    context_object_name = "skills"

    def get_queryset(self):
        """Return the list of skills for the logged in user.

        Returns:
            A queryset of the skills for the logged in user.
        """
        return Skill.objects.filter(owner=self.request.user)


class SkillDetailView(LoginRequiredMixin, DetailView):
    """A view to display the detail of a skill.

    LoginRequiredMixin: A mixin to require the user to be logged in.

    Attributes:
        model: A model to represent the skills.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    template_name = "skills/skill_detail.html"
    context_object_name = "skill"


class SkillUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """A view to update the detail of a skill.

    LoginRequiredMixin: A mixin to require the user to be logged in.
    UserPassesTestMixin: Uses the test_func method to restrict non-skill
                        owners from editing a skill.

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

    def test_func(self):
        """A method to check if the current user is the owner of the skill.

        Returns:
            A boolean value to check if the current user is the owner of the skill.
        """
        skill = self.get_object()
        return self.request.user == skill.owner


class SkillDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """A view to delete the specified skill.

    LoginRequiredMixin: A mixin to require the user to be logged in.
    UserPassesTestMixin: Uses the test_func method to restrict non-skill
                        owners from editing a skill.

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

    def test_func(self):
        """A method to check if the current user is the owner of the skill.

        Returns:
            A boolean value to check if the current user is the owner of the skill.
        """
        skill = self.get_object()
        return self.request.user == skill.owner


class SkillCreateView(LoginRequiredMixin, CreateView):
    """A view to create a new skill by only logged in users.

    LoginRequiredMixin: A mixin to require the user to be logged in.

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
    )
    template_name = "skills/skill_create.html"
    context_object_name = "skill"

    def form_valid(self, form):
        """A method to set the owner of the skill, by default,
        to the current logged in user creating the skill.

        Args:
            form: A form to represent the skill.

        Returns:
            A response to the form.
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)
