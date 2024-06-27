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
from django.shortcuts import redirect
from django.utils import timezone

from .models import Skill
from .forms import (
    SkillForm,
    SkillSearchForm,
    SkillDealForm,
    SkillDeal,
    SkillDealAcceptForm,
)


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
            if search_term:
                skillset = skillset.filter(
                    Q(name__icontains=search_term)
                    | Q(description__icontains=search_term)
                )
            else:
                skillset = Skill.objects.none()

        # If category is used
        elif self.request_path.startswith("/skills/categories/") and self.category:
            skillset = skillset.filter(category__name__iexact=self.category)

        elif self.request_path == "/skills/all":
            skillset = skillset

        else:
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

    def get_context_data(self, **kwargs: str) -> dict[str, str]:
        """Tracks the context of the current skill whose details page
        is active. It gets the skill object and the current user and uses
        both to check if a deal exists for the current user and skill.
        Then, it adds the result to the context data which is accessible
        in the template.

        Returns:
            A dictionary of the context data.
        """
        context = super().get_context_data(**kwargs)
        skill = self.get_object()
        user = self.request.user
        pending_deal = SkillDeal.objects.filter(
            skill=skill, provider=user, status=SkillDeal.PENDING
        ).first()
        context["pending_deal"] = pending_deal
        # context["deal_exists"] = pending_deal is not None
        context["deal_exists"] = skill.deal_exists_for_user(user)
        return context


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


class SkillDealCreateView(LoginRequiredMixin, CreateView):
    """Create a new skill deal.

    LoginRequiredMixin: A mixin to require the user to be logged in.

    Attributes:
        model: A model to represent the skill deal.
        fields: A tuple to represent the fields that can be edited.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = SkillDeal
    form_class = SkillDealForm

    def form_valid(self, form):
        """Set the owner and status of the skill deal.

        Args:
            form: A form to represent the skill deal.

        Returns:
            A response to the form.
        """
        skill = Skill.objects.get(pk=self.kwargs["skill_pk"])
        form.instance.skill = skill
        form.instance.provider = skill.owner
        form.instance.owner = self.request.user
        form.instance.status = SkillDeal.PENDING
        # Send a notification to the provider (to be implemented)
        # NotifyProvider(skill.owner, self.request.user, skill)
        return super().form_valid(form)

    def get(self, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        """A method to handle GET requests to the view by creating a deal without
        reendering the form."""
        form = self.get_form()
        return self.form_valid(form)

    def get_success_url(self) -> str:
        """Return to the user's list of skill deals after successfully
        creating a new deal."""
        return redirect("skill_deal_list")


class SkillDealAcceptView(LoginRequiredMixin, UpdateView):
    """Accept a skill deal request."""

    model = SkillDeal
    form_class = SkillDealAcceptForm

    def form_valid(self, form):
        """Accept the deal by updating the deal status"""
        form.instance.status = SkillDeal.ACTIVE
        form.instance.start_date = timezone.now()
        return super().form_valid(form)

    def get_object(self) -> SkillDeal:
        """Return the skill deal object."""
        return SkillDeal.objects.get(
            pk=self.kwargs["deal_pk"], provider=self.request.user
        )

    def get_success_url(self) -> str:
        return redirect("skill_deal_list")


class SkillDealListView(LoginRequiredMixin, ListView):
    """List all skill deals for the current logged in user
    - both deals that the user has requested and ones providing."""

    model = SkillDeal
    template_name = "skills/skill_deal_list.html"
    context_object_name = "skill_deals"

    def get_queryset(self) -> SkillDeal:
        """Return the list of skill deals for the currect user.

        Returns:
            SkillDeal: The skill deals object.
        """
        all_deals = SkillDeal.objects.all()
        return all_deals.filter(
            Q(owner=self.request.user) | Q(requester=self.request.user)
        )


class SkillDealDetailView(LoginRequiredMixin, DetailView):
    """A view to display the detail of a skill deal.

    LoginRequiredMixin: A mixin to require the user to be logged in.

    Attributes:
        model: A model to represent the skill deals.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = SkillDeal
    template_name = "skills/skill_deal_detail.html"
    context_object_name = "skill_deal"


class SkillDealUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """A view to update the detail of a skill deal.

    LoginRequiredMixin: A mixin to require the user to be logged in.
    UserPassesTestMixin: Uses the test_func method to ensure only the deal
                        requester can update the deal.

    Attributes:
        model: A model to represent the skill deals.
        fields: A tuple to represent the fields that can be edited.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = SkillDeal
    form_class = SkillDealForm
    template_name = "skills/skill_deal_form.html"

    def test_func(self):
        """A method to ensure only the requester of the skill deal (i.e. the owner)
        can update the details of the deal.

        Returns:
            A boolean value.
        """
        skill_deal = self.get_object()
        return self.request.user == skill_deal.owner

    def get_success_url(self) -> str:
        """URL to redirect the user to the skill deal detail page after they've
        successfully update the skill deal"""
        return reverse_lazy("skill_deal_detail", kwargs={"pk": self.kwargs["pk"]})


class SkillDealCompleteView(LoginRequiredMixin, UpdateView):
    """A view to complete a skill deal."""

    model = SkillDeal
    fields = ["status"]
    template_name = "skills/skill_deal_complete.html"

    def form_valid(self, form):
        """Update the deal status"""
        form.instance.status = SkillDeal.COMPLETED
        form.instance.end_date = timezone.now()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return redirect("skill_deal_list")
