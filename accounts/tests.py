from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.paginator import Paginator


from .models import UserProfile
from skills.models import Skill, SkillDeal, Message
from .forms import UserProfileForm


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


class ProfileViewTests(TestCase):
    """Tests for the ProfileView."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword123",
        )
        self.profile_url = reverse("profile", kwargs={"user_id": self.user.id})
        self.client.login(username="testuser", password="testpassword123")

    def test_profile_view_get(self):
        """Test that the profile view renders the correct template and context."""
        profile = UserProfile.objects.create(
            user=self.user, bio="This is a test bio.", location="Test Location"
        )
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile.html")
        self.assertEqual(response.context["profile"], profile)

    def test_profile_view_creates_minimal_profile_if_not_exists(self):
        """Test that a minimal profile is created if one does not exist."""
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())
        response = self.client.get(self.profile_url)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        self.assertEqual(response.status_code, 200)

    def test_profile_view_only_accessible_by_owner(self):
        """Test that a user can only view their own profile."""
        profile_url_other_user = reverse(
            "profile", kwargs={"user_id": self.other_user.id}
        )
        response = self.client.get(profile_url_other_user)
        self.assertEqual(response.status_code, 403)

    def test_profile_view_displays_correct_information(self):
        """Test that the profile view displays the correct user profile information."""
        profile = UserProfile.objects.create(
            user=self.user,
            bio="This is a test bio.",
            location="Test Location",
            phone_number="123456789",
        )
        response = self.client.get(self.profile_url)
        self.assertContains(response, "testuser")
        self.assertContains(response, "This is a test bio.")
        self.assertContains(response, "Test Location")
        self.assertContains(response, "123456789")

    def test_profile_view_displays_default_profile_image(self):
        """Test that the profile view displays the default profile image if none is uploaded."""
        response = self.client.get(self.profile_url)
        self.assertContains(response, 'src="')

    def test_profile_view_displays_uploaded_profile_image(self):
        """Test that the profile view displays the uploaded profile image."""
        profile_image = SimpleUploadedFile(
            name="test_image.jpg", content=b"", content_type="image/jpeg"
        )
        UserProfile.objects.create(user=self.user, profile_image=profile_image)
        response = self.client.get(self.profile_url)
        self.assertContains(response, "<img")
        self.assertContains(response, 'src="')


class ProfileUpdateViewTests(TestCase):
    """Tests for the ProfileUpdateView."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword123",
        )
        self.profile = UserProfile.objects.create(
            user=self.user, bio="This is a test bio.", location="Test Location"
        )
        self.update_url = reverse("profile_update", kwargs={"user_id": self.user.id})
        self.client.login(username="testuser", password="testpassword123")

    def test_profile_update_view_get(self):
        """Test that the profile update view renders the correct template and context."""
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/profile_update.html")
        self.assertIsInstance(response.context["form"], UserProfileForm)

    def test_profile_update_view_only_accessible_by_owner(self):
        """Test that a user can only update their own profile."""
        update_url_other_user = reverse(
            "profile_update", kwargs={"user_id": self.other_user.id}
        )
        response = self.client.get(update_url_other_user)
        self.assertEqual(response.status_code, 403)

    def test_profile_update_view_post_valid_form(self):
        """Test that a valid profile update form updates the profile and redirects correctly."""
        updated_data = {
            "bio": "Updated bio",
            "location": "Updated location",
            "phone_number": "987654321",
            "skills_offered": "Updated skills",
            "availability": "Updated availability",
        }
        response = self.client.post(self.update_url, updated_data)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "Updated bio")
        self.assertEqual(self.profile.location, "Updated location")
        self.assertEqual(self.profile.phone_number, "987654321")
        self.assertEqual(self.profile.skills_offered, "Updated skills")
        self.assertEqual(self.profile.availability, "Updated availability")
        self.assertRedirects(
            response, reverse("profile", kwargs={"user_id": self.user.id})
        )

    def test_profile_update_view_displays_correct_information(self):
        """Test that the profile update view displays the current user profile information."""
        response = self.client.get(self.update_url)
        self.assertContains(response, "This is a test bio.")
        self.assertContains(response, "Test Location")
        self.assertContains(response, "Update Profile")
        self.assertContains(response, "Cancel")


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.url = reverse("dashboard", kwargs={"user_id": self.user.id})
        self.client.login(username="testuser", password="testpassword123")

    def test_dashboard_view_accessible(self):
        """Test that the dashboard view is accessible."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view_uses_correct_template(self):
        """Test that the dashboard view uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_dashboard_view_context_contains_user(self):
        """Test that the context contains the user object."""
        response = self.client.get(self.url)
        self.assertIn("user", response.context)
        self.assertEqual(response.context["user"], self.user)

    def test_dashboard_view_context_contains_current_date(self):
        """Test that the context contains the current date."""
        response = self.client.get(self.url)
        self.assertIn("current_date", response.context)

    def test_dashboard_view_context_contains_greeting(self):
        """Test that the context contains the greeting."""
        response = self.client.get(self.url)
        self.assertIn("greeting", response.context)
