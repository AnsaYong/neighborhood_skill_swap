from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "credits",
        "is_staff",
    ]  # Set a list of fields to display in the admin panel.
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "profile_image",
                    "bio",
                    "location",
                    "phone_number",
                    "skills_offered",
                    "availability",
                    "credits",
                )
            },
        ),
    )  # Add all new fields to fields used in editing users
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": (
                    "profile_image",
                    "bio",
                    "location",
                    "phone_number",
                    "skills_offered",
                    "availability",
                    "credits",
                )
            },
        ),
    )  # Add all new fields to fields used in adding users


admin.site.register(
    CustomUser, CustomUserAdmin
)  # Register the CustomUser model with the CustomUserAdmin options
