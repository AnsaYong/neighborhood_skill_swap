from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout
from .models import UserProfile, CustomUser
from .forms import UserProfileForm, CustomUserCreationForm
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    """A class-based view to handle user login.

    Methods:
        get_success_url: A method to get the URL to redirect to after a successful login.
    """

    def get_success_url(self):
        """Get the URL to redirect to after a successful login."""
        return reverse("profile", kwargs={"user_id": self.request.user.id})


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


class ProfileDecisionView(View):
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


class ProfileCreateView(CreateView):
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
        # Check if the user already has a profile
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


class ProfileView(DetailView):
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
        """Get the user profile object.

        Returns:
            UserProfile: The user profile object.
        """
        try:
            return UserProfile.objects.get(user__id=self.kwargs["user_id"])
        except UserProfile.DoesNotExist:
            # Create a minimal user profile if one does not exist
            user = CustomUser.objects.get(id=self.kwargs["user_id"])
            return UserProfile.objects.create(user=user)
