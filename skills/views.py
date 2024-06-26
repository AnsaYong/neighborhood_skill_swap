from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    CreateView,
)
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Skill
from .forms import SkillForm, SkillSearchForm


# Create your views here.
class SkillListView(LoginRequiredMixin, ListView):
    """Displays a list of skills based on the request path:
        - path 1: through search bar.
        - path 2: based on a category.
        - path 3: based on the logged in user.

    LoginRequiredMixin: A mixin to require the user to be logged in.

    Attributes:
        model: A model to represent the skills.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    template_name = "skills/skill_list.html"
    form_class = SkillSearchForm
    context_object_name = "skills"

    def dispatch(self, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        """Overrides the dispatch method to differentiate the
        request path.

        Args:
            request: An HttpRequest object.
            args: A tuple of arguments.
            kwargs: A dictionary of keyword arguments.
        """
        self.request_path = request.path
        self.category = kwargs.get("category", None)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> Skill:
        """Return the list of skills based on a searched named, otherwise
        the skills of the logged in user by default.

        Returns:
            Skill: Object of the user requested skills.
        """
        skillset = Skill.objects.all()
        search_term = self.request.GET.get("search_term")
        print(f"search term in get_queryset: {search_term}")

        # If search bar is used
        if self.request_path == "/skills/search/":
            print(f"Filtering using search term: {search_term}")
            if search_term:
                skillset = skillset.filter(
                    Q(name__icontains=search_term)
                    | Q(description__icontains=search_term)
                )
            else:
                skillset = Skill.objects.none()

        # If category is used
        elif self.request_path.startswith("/skills/categories/") and self.category:
            print(f"category to use in filtering skills: {self.category}")
            skillset = skillset.filter(category__name__iexact=self.category)

        elif self.request_path == "/skills/all":
            skillset = skillset

        else:
            print(f"Filtering skills based on logged in user")
            skillset = skillset.filter(owner=self.request.user)

        return skillset

    def get_context_data(self, **kwargs: str) -> dict[str, str]:
        """A method to add a search form to the default context data
        so that users are able to search for specific skills.

        Returns:
            A dictionary of the context data.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = SkillSearchForm(self.request.GET or None)
        search_term = self.request.GET.get("search_term")
        print(f"search term in get_context_data: {search_term}")

        if (
            self.request_path == "/skills/search/"
            and search_term
            and not context["skills"]
        ):
            context["no_results"] = "No skills matched your search criteria."

        return context


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
    The new skill_type is set automatically based on the request path.

    LoginRequiredMixin: A mixin to require the user to be logged in.

    Attributes:
        model: A model to represent the skills.
        form_class: A form to represent the skill.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Skill
    form_class = SkillForm
    template_name = "skills/skill_create.html"
    context_object_name = "skill"

    def dispatch(self, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        """Overrides the dispatch method to differentiate the
        request path.

        Args:
            request: An HttpRequest object.
            args: A tuple of arguments.
            kwargs: A dictionary of keyword arguments.
        """
        self.request_path = request.path
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """A method to set the owner of the skill, by default,
        to the current logged in user creating the skill.

        Args:
            form: A form to represent the skill.

        Returns:
            A response to the form.
        """
        if self.request_path == "/skills/new/wanted/":
            form.instance.skill_type = "wanted"
        else:
            form.instance.skill_type = "offered"

        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        """Customize the fields displayed by the form based on the URL."""
        form = super().get_form(form_class)
        if self.request_path == "/skills/new/wanted/":
            form.fields.pop("Level")
            form.fields.pop("description")
        return form
