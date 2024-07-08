from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
