from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
    CreateView,
)

from .models import Skill, SkillDeal, Review
from .forms import SkillForm, SkillSearchForm, ReviewForm


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
        self.skill_type = kwargs.get("skill_type", None)
        self.category = kwargs.get("category", None)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> Skill:
        """Return the list of skills based on a searched named, otherwise
        the skills of the logged in user by default.

        Returns:
            Skill: Object of the user requested skills.
        """
        skillset_all_other_users = Skill.objects.exclude(
            Q(owner=self.request.user) | Q(skill_type="wanted")
        )
        skillset_user = Skill.objects.filter(owner=self.request.user)
        skillset_all = Skill.objects.all()

        search_term = self.request.GET.get("search_term")

        # If search bar is used do not show current user's skills
        if self.request_path == "/skills/search/":
            if search_term:
                skillset = skillset_all_other_users.filter(
                    Q(name__icontains=search_term)
                    | Q(description__icontains=search_term)
                )
            else:
                skillset = Skill.objects.none()

        # If category is used do not show current user's skills
        elif self.request_path.startswith("/skills/categories/") and self.category:
            skillset = skillset_all_other_users.filter(
                category__name__iexact=self.category
            )

        elif self.request_path == "/skills/wanted":
            skillset = skillset_user.filter(skill_type="wanted")

        elif self.request_path == "/skills/offered":
            skillset = skillset_user.filter(skill_type="offered")

        elif self.request_path == "/skills/all":
            skillset = skillset_all

        else:
            pass

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

        # Get pending deal requests for this skill
        pending_deals = SkillDeal.objects.filter(skill=skill, status=SkillDeal.PENDING)
        context["pending_deals"] = pending_deals
        context["deal_exists"] = skill.deal_exists_for_user(user)

        # Get reviews for this skill
        reviews = Review.objects.filter(skill=skill)
        reviews_count = reviews.count()
        context["reviews"] = reviews
        context["reviews_count"] = reviews_count

        return context


class SkillReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """A view to create a new review for a skill.
    UserpassesTestMixin ensures that only a user who has made use of the
    skill can review it.

    LoginRequiredMixin ensures the user rating the skill is logged in.

    Attributes:
        model: A model to represent the reviews.
        fields: A tuple to represent the fields that can be edited.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    model = Review
    form_class = ReviewForm
    template_name = "skills/skill_review_create.html"
    context_object_name = "review"

    def test_func(self):
        """A method to check if the current user has made use of the skill.

        Returns:
            A boolean value to check if the current user has made use of the skill.
        """
        skill = get_object_or_404(Skill, pk=self.kwargs["pk"])
        return SkillDeal.objects.filter(
            skill=skill, owner=self.request.user, status=SkillDeal.COMPLETED
        ).exists()

    def form_valid(self, form):
        """A method to set the owner of the review, by default,
        to the current logged in user creating the review.

        Args:
            form: A form to represent the review.

        Returns:
            A response to the form.
        """
        form.instance.owner = self.request.user
        form.instance.skill = get_object_or_404(Skill, pk=self.kwargs["pk"])
        response = super().form_valid(form)
        print(f"My rating is: {form.instance.rating}")
        form.instance.skill.update_rating(form.instance.rating)
        return response

    def get_context_data(self, **kwargs):
        """A method to add the skill object to the context data so that
        it can be accessed in the template.

        Returns:
            A dictionary of the context data.
        """
        context = super().get_context_data(**kwargs)
        context["skill"] = get_object_or_404(Skill, pk=self.kwargs["pk"])
        return context

    def get_success_url(self) -> str:
        """URL to redirect the user to the skill detail page after they've
        successfully reviewed the skill"""
        return reverse_lazy("skill_detail", kwargs={"pk": self.kwargs["pk"]})


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
    context_object_name = "skill"

    def get_success_url(self):
        """A method to redirect to the skills page after deleting a skill.

        Returns:
            A string to represent the URL to redirect to after deleting the skill.
        """
        if self.object.skill_type == "offered":
            return reverse_lazy("skills", kwargs={"skill_type": "offered"})
        elif self.object.skill_type == "wanted":
            return reverse_lazy("skills", kwargs={"skill_type": "wanted"})

    def delete(self, request, *args, **kwargs):
        """Override the delete method to use a dynamic URL for redirection."""
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

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

    def get_success_url(self):
        """Overriding the default success URL to redirect to the skills page
        - wanted or offered based on the type of skilll created."""
        if self.request_path == "/skills/new/wanted/":
            return reverse_lazy("skills", kwargs={"skill_type": "wanted"})
        else:
            return reverse_lazy("skills", kwargs={"skill_type": "offered"})

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
            form.fields.pop("level")
            form.fields.pop("description")
        return form
