from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users. Includes all the required fields,
    plus a repeated password.
    """

    class Meta(UserCreationForm.Meta):
        """Meta class for CustomUserCreationForm which specifies extra fields
        in addition to the default ones.

        Attributes:
            model: The model to use for the form.
            fields: The fields to include in the form.
        """

        model = CustomUser
        fields = (
            "username",
            "email",
        )


class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on the user, but
    replaces the password field with admin's password hash display field.
    """

    class Meta(UserChangeForm.Meta):
        """Meta class for CustomUserChangeForm which specifies extra fields
        in addition to the default ones.

        Attributes:
            model: The model to use for the form.
            fields: The fields to include in the form.
        """

        model = CustomUser
        fields = (
            "username",
            "email",
            "age",
        )


class UserProfileForm(forms.ModelForm):
    """A form for updating user profiles. Includes all the fields on the user profile,
    except `credits` which is updated automatically.
    """

    class Meta:
        """Meta class for UserProfileForm which specifies the model and fields to include in the form.

        Attributes:
            model: The model to use for the form.
            fields: The fields to include in the form.
        """

        model = UserProfile
        fields = [
            "profile_image",
            "bio",
            "location",
            "phone_number",
            "skills_offered",
            "availability",
        ]
