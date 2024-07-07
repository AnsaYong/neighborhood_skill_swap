from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm


class UserProfileInline(admin.StackedInline):
    """A class to represent the user profile inline in the admin interface.
    It is used to display and edit the UserProfile fields within the
    CustomUser.

    Attributes:
        model: The model to use for the inline.
        can_delete: A boolean to determine if the inline can be deleted.
        verbose_name_plural: A string to represent the verbose name of the inline.
        fk_name: The name of the foreign key field.
        fields: The fields to include in the inline.
    """

    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    fields = [
        "profile_image",
        "bio",
        "phone_number",
        "skills_offered",
        "availability",
        "credits",
    ]


class CustomUserAdmin(UserAdmin):
    """A class to represent the CustomUser admin interface that allows
    the admin to create and edit users.

    Attributes:
        add_form: The form to use for adding a CustomUser.
        form: The form to use for updating a CustomUser.
        model: The model to use for the admin.
        list_display: A list of fields to display in the admin interface.
        fieldsets: A list of fieldsets to display in the admin interface.
        add_fieldsets: A list of fieldsets to display when adding a new CustomUser.
        inlines: A list of inline classes to include in the admin interface.
    """

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["username", "email", "age", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("age",)}),
    )  # Add the location field to fields used in editing users
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("email",)}),
    )  # Add the location field to fields listed during signup
    inlines = [UserProfileInline]

    def get_inline_instances(self, request, obj=None):
        """A method to get the inline instances for the CustomUserAdmin.
        It ensures that the inline UserProfile is only displayed when
        editing an existing user, not when creating a new one.

        Args:
            request: The request object.
            obj: The object being edited.
        """
        if not obj:
            return []
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """A class to represent the UserProfile admin interface that allows
    the admin to create and edit user profiles separately.

    Attributes:
        list_display: A list of fields to display in the admin interface.
    """

    list_display = [
        "user",
        "bio",
        "location",
        "phone_number",
        "skills_offered",
        "availability",
        "credits",
    ]
