from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
)

from .models import Skill, SkillDeal, Review
from .forms import SkillDealForm


# Create your views here.
class SkillDealCreateView(LoginRequiredMixin, View):
    """Create a new skill deal.

    LoginRequiredMixin: A mixin to require the user to be logged in.

    Attributes:
        model: A model to represent the skill deal.
        fields: A tuple to represent the fields that can be edited.
        template_name: A string to represent the template file.
        context_object_name: A string to represent the context object name.
    """

    def get(self, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        """Handle GET requests.

        Create a new skill deal by automatically setting the skill, owner, provider,
        and status of the deal in a new SkillDeal object.
        """
        skill = get_object_or_404(Skill, pk=self.kwargs["skill_pk"])
        skill_deal = SkillDeal.objects.create(
            skill=skill,
            owner=self.request.user,
            provider=skill.owner,
            status=SkillDeal.PENDING,
        )
        skill_deal.send_message_on_request()
        # Optionally, send a notification to the provider here
        # NotifyProvider(skill.owner, self.request.user, skill)
        return redirect("skill_detail", pk=self.kwargs["skill_pk"])


class SkillDealAcceptView(LoginRequiredMixin, View):
    """Accept a skill deal request."""

    def get(self, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        """Handle GET requests.

        Accept a skill deal request by updating the status of the existing deal
        to ACTIVE.
        """
        deal = get_object_or_404(SkillDeal, pk=self.kwargs["deal_pk"])
        deal.accept_deal()
        return redirect("provided_deals")


class SkillDealListView(LoginRequiredMixin, ListView):
    """List of all skill deals for the current logged-in user
    - both deals that the user has requested and ones providing."""

    model = SkillDeal
    template_name = "skills/skill_deal_list.html"
    context_object_name = "my_deals"

    def get_queryset(self):
        """Return a list of skill deals for the current logged-in user."""
        user = self.request.user
        filter_type = self.kwargs.get("filter_type", "all")

        if filter_type == "provided":
            queryset = SkillDeal.objects.filter(provider=user)
        elif filter_type == "requested":
            queryset = SkillDeal.objects.filter(owner=user)
        else:
            queryset = SkillDeal.objects.filter(Q(provider=user) | Q(owner=user))

        reviewed_skills = Review.objects.filter(owner=user).values_list(
            "skill_id", flat=True
        )
        queryset = queryset.exclude(
            Q(status=SkillDeal.COMPLETED) & Q(skill_id__in=reviewed_skills)
        )

        return queryset

    def get_context_data(self, **kwargs):
        """Add the filter type to the context."""
        context = super().get_context_data(**kwargs)
        context["filter_type"] = self.kwargs.get("filter_type", "all")
        return context


class ProvidedDealsView(SkillDealListView):
    """View for deals where the user is the skill provider"""

    def get_queryset(self):
        """Return a list of skill deals where the user is the provider."""
        user = self.request.user
        rated_skills = Review.objects.filter(owner=user).values_list(
            "skill_id", flat=True
        )

        return SkillDeal.objects.filter(
            provider=user,
            status__in=[
                SkillDeal.PENDING,
                SkillDeal.ACTIVE,
                SkillDeal.COMPLETED,
                SkillDeal.CANCELLED,
            ],
        ).exclude(Q(status=SkillDeal.COMPLETED) & Q(skill_id__in=rated_skills))


class RequestedDealsView(SkillDealListView):
    """View for deals where the user is the skillDeal owner (skill requestor)"""

    def get_queryset(self):
        """Return a list of skill deals where the user is the owner."""
        user = self.request.user
        rated_skills = Review.objects.filter(owner=user).values_list(
            "skill_id", flat=True
        )

        queryset = SkillDeal.objects.filter(
            owner=user,
            status__in=[
                SkillDeal.PENDING,
                SkillDeal.ACTIVE,
                SkillDeal.COMPLETED,
                SkillDeal.CANCELLED,
            ],
        ).exclude(Q(status=SkillDeal.COMPLETED) & Q(skill_id__in=rated_skills))

        return queryset


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
    """A view to complete a skill deal.

    Calls the mark_complete() method on the SkillDeal object which updates
    the specified skill deal's status and end_date attibutes."""

    def get(self, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        """Handle GET requests.

        Complete a skill deal by updating the status of the existing deal
        to COMPLETED and setting the end date to the current date.
        """
        deal = get_object_or_404(SkillDeal, pk=self.kwargs["deal_pk"])
        deal.mark_complete()
        return redirect("skill_deal_list")


class SkillDealRejectView(LoginRequiredMixin, View):
    """Reject a skill deal request."""

    def get(self, request: HttpRequest, *args: str, **kwargs: str) -> HttpResponse:
        """Handle GET requests.

        Reject a skill deal request by updating the status of the existing deal
        to CANCELLED.
        """
        deal = get_object_or_404(SkillDeal, pk=self.kwargs["deal_pk"])
        deal.cancel_deal()
        return redirect("provided_deals")
