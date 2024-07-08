from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class SignupViewTests(TestCase):
    """Tests for the user authentication views."""

    def setUp(self):
        """Set up the data needed for the tests."""
        self.signup_url = reverse("signup")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        self.existing_user = get_user_model().objects.create_user(
            username="existinguser",
            email="existinguser@example.com",
            password="testpassword123",
        )

    def test_signup_view_get(self):
        """Test that the signup view renders the signup html."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_view_post_valid_form(self):
        """Test that a valid signup form creates a new user and
        they are correctly redirected to the profile-decision page."""
        response = self.client.post(self.signup_url, self.user_data)

        # Ensure user was created
        self.assertTrue(
            get_user_model()
            .objects.filter(username=self.user_data["username"])
            .exists()
        )
        self.assertRedirects(response, reverse("profile_decision"))

    def test_signup_view_post_invalid_form(self):
        """Test that an invalid data combination in the signup form
        does not create a user."""
        invalid_data = {
            "username": "testuser",
            "password1": "password@123",
            "password2": "differentpassword",
        }
        response = self.client.post(self.signup_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")
        self.assertFalse(
            get_user_model()
            .objects.filter(username=self.user_data["username"])
            .exists()
        )

    def test_signup_view_post_existing_user(self):
        """Test that a user cannot be created with an existing username."""
        self.client.post(self.signup_url, self.user_data)
        response = self.client.post(self.signup_url, self.user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")
        self.assertEqual(
            response.context["form"].errors["username"][0],
            "A user with that username already exists.",
        )


class CustomLoginViewTests(TestCase):
    """Tests for the login view."""

    def setUp(self):
        """Set up the data needed for the tests."""
        self.login_url = reverse("login")
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )

    def test_login_url_resolves(self):
        """Test that the login view resolves to the correct view."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.login_url, "/accounts/login/")
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_view_post_valid_credentials(self):
        """Test that a valid login form logs the user in."""
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "testpassword123"}
        )

        self.assertRedirects(
            response, reverse("dashboard", kwargs={"user_id": self.user.id})
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_post_invalid_credentials(self):
        """Test that a user cannot log in with invalid credentials."""
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class CustomLogoutViewTests(TestCase):
    """Tests for the CustomLogoutView."""

    def setUp(self):
        self.logout_url = reverse("logout")
        self.home_url = reverse("home")
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )

    def test_logout_url_resolves(self):
        """Test that the logout URL resolves correctly."""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.home_url)

    def test_logout_view_logs_out_user(self):
        """Test that a logged-in user is logged out after accessing the logout view."""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.home_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class ProfileDecisionViewTests(TestCase):
    """Tests for the ProfileDecisionView."""

    def setUp(self):
        self.profile_decision_url = reverse("profile_decision")
        self.profile_create_url = reverse("profile_create")
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.client.login(username="testuser", password="testpassword123")

    def test_profile_decision_view_get(self):
        """Test that the profile decision view correctly renders the
        profile_decision.html."""
        response = self.client.get(self.profile_decision_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile_decision.html")

    def test_profile_decision_view_post_create_profile(self):
        """Test that the user is redirected to the profile create page if
        they choose to create a profile."""
        response = self.client.post(self.profile_decision_url, {"create_profile": ""})
        self.assertRedirects(response, self.profile_create_url)

    def test_profile_decision_view_post_skip_profile(self):
        """Checks that a new UserProfile is created and the user is redirected
        to their profile page when they choose to skip creating a profile."""
        profile_url = reverse("profile", kwargs={"user_id": self.user.id})
        response = self.client.post(self.profile_decision_url, {"skip_profile": ""})
        self.assertRedirects(response, profile_url)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())


class ProfileCreateViewTests(TestCase):
    """Tests for the ProfileCreateView."""

    def setUp(self):
        self.profile_create_url = reverse("profile_create")
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.client.login(username="testuser", password="testpassword123")

    def test_profile_create_view_get(self):
        """Test that the profile create view renders correctly."""
        response = self.client.get(self.profile_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile_create.html")

    def test_profile_create_view_post_valid_form(self):
        """Test that a valid profile form creates a new profile."""
        profile_data = {
            "bio": "This is a test bio.",
            "location": "Test Location",
            "phone_number": "0844437287",
        }
        response = self.client.post(self.profile_create_url, profile_data)
        profile_url = reverse("profile", kwargs={"user_id": self.user.id})
        self.assertRedirects(response, profile_url)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        self.assertTrue(
            UserProfile.objects.filter(
                user=self.user,
                bio=profile_data["bio"],
                location=profile_data["location"],
                phone_number=profile_data["phone_number"],
            ).exists()
        )

    def test_profile_create_view_redirect_if_profile_exists(self):
        """Test that the user is redirected if they already have a profile."""
        UserProfile.objects.create(user=self.user, bio="Existing bio")
        response = self.client.get(self.profile_create_url)
        profile_url = reverse("profile", kwargs={"user_id": self.user.id})
        self.assertRedirects(response, profile_url)
