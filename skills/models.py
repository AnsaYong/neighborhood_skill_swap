from django.db import models
from django.conf import settings
from django.urls import reverse


# Create your models here.
class Category(models.Model):
    """A model to represent the category of the skills.

    Attributes:
        name: A CharField to represent the name of the category.
    """

    name = models.CharField(max_length=100, unique=True, blank=False)

    def __str__(self):
        """Return a string representation of the category."""
        return self.name


class Rating(models.Model):
    """A model to represent the rating of the skills.

    Attributes:
        skill: A ForeignKey to represent the skill that is rated.
        user: A ForeignKey to represent the user who rated the skill.
        rating: A float to represent the rating of the skill.

    """

    skill = models.ForeignKey("Skill", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        """Return a string representation of the rating."""
        return f"{self.skill} - {self.rating}"


class Skill(models.Model):
    """A model to represent user's skills.

    Attributes:
        name: A CharField to represent the name of the skill.
        category: A CharField to represent the category of the skill for the user.
        Level: A CharField to represent the level of the skill for the user.
        description: A TextField to represent the description of the skill.
        date: A DateTimeField to represent the date the skill was created.
        owner: A ForeignKey to represent the user who owns the skill.
        rating: A float to represent the rating of the skill.
    """

    name = models.CharField(max_length=100, blank=False)
    Level = models.CharField(max_length=20, blank=False)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the skill."""
        return self.name

    def get_absolute_url(self):
        """Return the absolute URL of the skill."""
        return reverse("skill_detail", kwargs={"pk": self.pk})
