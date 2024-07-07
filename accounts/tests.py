from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class SignupViewTests(TestCase):
    """Tests for the signup view."""

    def setUp(self):
        self.signup_url = reverse("signup")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }

    def test_signup_view_get(self):
        """Test that the signup view renders the signup form."""
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
