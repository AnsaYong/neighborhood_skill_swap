from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    """A custom user model that extends the AbstractUser model.

    Attributes:
        age: An integer field to store the user's age.
    """

    age = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        """String representation of the user model."""
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )  # A one-to-one link to the user model
    profile_image = models.ImageField(
        upload_to="profile_images/", null=True, blank=True
    )  # A field to upload a profile image
    location = models.CharField(
        max_length=255, blank=True
    )  # Information about where the user is located (could be a city, region, or specific address)
    bio = models.TextField(
        max_length=500, blank=True
    )  # A short biography or description about the user.
    phone_number = models.CharField(
        max_length=20, blank=True
    )  # A phone number for contact purposes
    skills_offered = models.TextField(
        max_length=500, blank=True
    )  # A field to summarize the skills the user offers
    availability = models.CharField(
        max_length=255, blank=True
    )  # Information about the user's general availability (e.g., evenings, weekends)
    credits = models.IntegerField(
        default=0
    )  # Field to store the number of credits a user has

    def __str__(self):
        return self.user.username
