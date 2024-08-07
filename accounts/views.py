from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Q

from .models import UserProfile, CustomUser
from .forms import UserProfileForm, CustomUserCreationForm
from skills.models import Skill, SkillDeal, Message, Notification


class CustomLoginView(LoginView):
    """A class-based view to handle user login.

    Methods:
        get_success_url: A method to get the URL to redirect to after a successful login.
    """

    def get_success_url(self):
        """Get the URL to redirect to after a successful login."""
        return reverse("dashboard", kwargs={"user_id": self.request.user.id})


class CustomLogoutView(View):
    """A class-based view to handle user logout.

    Methods:
        get: A method to handle GET requests to the view.
    """

    def get(self, request):
        """Handle GET requests to the view.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        logout(request)
        return redirect(reverse_lazy("home"))


class SignupView(View):
    """A class-based view to handle user signup.

    Methods:
        get: A method to handle GET requests to the view.
        post: A method to handle POST requests to the view.
    """

    def get(self, request):
        """Handle GET requests to the view.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        form = CustomUserCreationForm()
        return render(request, "registration/signup.html", {"form": form})

    def post(self, request):
        """Handle POST requests to the view.
        Creates a user profile if the form is valid.

        Args:
            request (HttpRequest): The request object.

        Returns:
            HttpResponse: The response object.
        """
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse_lazy("profile_decision"))
        return render(request, "registration/signup.html", {"form": form})


class ProfileDecisionView(UserPassesTestMixin, View):
    """A class-based view to get user to choose if they want to create
    a profile or not.

    Methods:
        get: A method to handle GET requests to the view.
        post: A method to handle POST requests to the view.
    """

    template_name = "registration/profile_decision.html"

    def get(self, request):
        """Handle GET requests to the view."""
        return render(request, self.template_name)

    def post(self, request):
        """Handle POST requests to the view.
        Redirects the new user to create a profile if they choose to do so,
        or to their minimal profile page created by default during signup,
        if they choose not to.
        """

        if "create_profile" in request.POST:
            return redirect(reverse_lazy("profile_create"))
        else:
            UserProfile.objects.create(user=request.user)
            return redirect(
                reverse_lazy("profile", kwargs={"user_id": request.user.id})
            )

    def test_func(self) -> bool:
        """Ensures only registered users can access the profile creation option.

        Returns:
            bool: True if the user is authenticated, False otherwise."""
        return self.request.user.is_authenticated


class ProfileCreateView(UserPassesTestMixin, CreateView):
    """A class-based view to create a user profile.

    Attributes:
        template_name: The name of the template to render.

    Methods:
        get: A method to handle GET requests to the view.
        post: A method to handle POST requests to the view.
    """

    model = UserProfile
    form_class = UserProfileForm
    template_name = "registration/profile_create.html"

    def dispatch(self, request, *args, **kwargs):
        """Check if the user already has a profile and
        redirect them if they do.
        """
        if UserProfile.objects.filter(user=request.user).exists():
            return redirect(
                reverse_lazy("profile", kwargs={"user_id": request.user.id})
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Save the user profile and associate it with the current user.

        Args:
            form (UserProfileForm): The form object.

        Returns:
            HttpResponseRedirect: The response object.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after a successful form submission.

        Returns:
            str: The URL to redirect to.
        """
        return reverse_lazy("profile", kwargs={"user_id": self.request.user.id})

    def test_func(self) -> bool:
        """Ensures only registered users can create a profile.

        Returns:
            bool: True if the user is authenticated, False otherwise."""
        return self.request.user.is_authenticated


class ProfileView(UserPassesTestMixin, DetailView):
    """A class-based view to display a user profile.

    Attributes:
        template_name: The name of the template to render.

    Methods:
        get: A method to handle GET requests to the view.
    """

    model = UserProfile
    template_name = "registration/profile.html"
    context_object_name = "profile"

    def get_object(self):
        """Get the user profile object to display on the user's profile page.

        Returns:
            UserProfile: The user profile object.
        """
        try:
            return UserProfile.objects.get(user__id=self.kwargs["user_id"])
        except UserProfile.DoesNotExist:
            # Create a minimal user profile if one does not exist
            user = CustomUser.objects.get(id=self.kwargs["user_id"])
            return UserProfile.objects.create(user=user)

    def test_func(self) -> bool:
        """Ensures registered users can only view their own profile."""
        return self.request.user.id == self.kwargs["user_id"]


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    """A class-based view to update a user profile.

    Attributes:
        model: The model to use in the view.
        form_class: The form class to use in the view.
        template_name: The name of the template to render.

    Methods:
        get_object: Get the user profile object.
        get_success_url: Return the URL to redirect to after a successful form submission.
    """

    model = UserProfile
    form_class = UserProfileForm
    template_name = "registration/profile_update.html"

    def get_object(self):
        """Get the user profile object based on the user's id.

        Returns:
            UserProfile: The user profile object so that it can be updated.
        """
        return UserProfile.objects.get(user__id=self.kwargs["user_id"])

    def form_valid(self, form):
        """Handle profile updates by updating the user profile object."""
        if "profile_image" in self.request.FILES:
            form.instance.profile_image = self.request.FILES["profile_image"]
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after a successful form submission.

        Returns:
            str: The URL to redirect to.
        """
        return reverse_lazy("profile", kwargs={"user_id": self.kwargs["user_id"]})

    def test_func(self) -> bool:
        """Ensures registered users can only update their own profile."""
        return self.request.user.id == self.kwargs["user_id"]


class DashboardView(UserPassesTestMixin, View):
    """A class-based view to display a user dashboard.
    Filters data to display on the dashboard.

    Methods:
        get: A method to handle GET requests to the view.
    """

    def get(self, request, user_id):
        """Handle GET requests to the view.
        - Adds the current date and greeting message to the context.
        - Filters the user's "wanted" skills and uses them to filter suggested skills.

        Args:
            request (HttpRequest): The request object.
            user_id (int): The user's ID.

        Returns:
            HttpResponse: The response object.
        """
        user = get_object_or_404(CustomUser, id=user_id)

        # Date and greeting message
        now = timezone.now()
        current_date = now.strftime("%A, %B %d, %Y")
        hour = now.hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # Skill suggestions
        wanted_skills = Skill.objects.filter(owner=user, skill_type="wanted")
        wanted_skills_names = [skill.name for skill in wanted_skills]
        selected_skills = (
            Skill.objects.filter(name__in=wanted_skills_names, skill_type="offered")
            .exclude(owner=user)
            .annotate(reviews_count=Count("review"))
        )

        # Pagination for suggested skills
        paginator = Paginator(selected_skills, 4)
        page_number = request.GET.get("page")
        suggested_skills = paginator.get_page(page_number)

        # Recent deals and unread messages
        # Query all deals related to the user as either provider or owner
        recent_deals = SkillDeal.objects.filter(
            Q(provider=user) | Q(owner=user)
        ).order_by("-created_at")[:3]
        print(recent_deals)

        # Unread messages
        unread_messages = Message.objects.filter(receiver=user, is_read=False).order_by(
            "-timestamp"
        )[:3]

        # Notification count
        unread_messages_count = unread_messages.count()
        pending_deals_count = SkillDeal.objects.filter(
            provider=user, status=SkillDeal.PENDING
        ).count()

        # Counting all deals related to the user
        pending_deals = SkillDeal.objects.filter(
            provider=user, status=SkillDeal.PENDING
        ).count()
        active_deals = SkillDeal.objects.filter(
            provider=user, status=SkillDeal.ACTIVE
        ).count()
        completed_deals = SkillDeal.objects.filter(
            provider=user, status=SkillDeal.COMPLETED
        ).count()
        cancelled_deals = SkillDeal.objects.filter(
            provider=user, status=SkillDeal.CANCELLED
        ).count()

        context = {
            "user": user,
            "suggested_skills": suggested_skills,
            "current_date": current_date,
            "greeting": greeting,
            "recent_deals": recent_deals,
            "unread_messages": unread_messages,
            "unread_messages_count": unread_messages_count,
            "pending_deals_count": pending_deals_count,
            "pending_deals": pending_deals,
            "active_deals": active_deals,
            "completed_deals": completed_deals,
            "cancelled_deals": cancelled_deals,
        }
        return render(request, "dashboard.html", context)

    def test_func(self) -> bool:
        """Ensures registered users can only view their own dashboard."""
        return self.request.user.id == self.kwargs["user_id"]
