from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Avg


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


class Skill(models.Model):
    """A model to represent user's skills.

    Attributes:
        name: A CharField to represent the name of the skill.
        level: A CharField to represent the level of the skill for the user.
        description: A TextField to represent the description of the skill.
        owner: A ForeignKey to represent the user who owns the skill.
        category: A CharField to represent the category of the skill for the user.
        date: A DateTimeField to represent the date the skill was created.
        skill_type: A CharField to represent the type of the skill (offered or wanted).
        rating: A float to represent the rating of the skill.
    """

    name = models.CharField(max_length=100, blank=False)
    level = models.CharField(max_length=20, blank=False)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    skill_type = models.CharField(max_length=20, blank=False)
    rating = models.FloatField(default=5.0)

    def update_rating(self):
        """Update the rating of the skill based on average of all reviews."""
        reviews = Review.objects.filter(skill=self)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"]
            if avg_rating is not None:
                # Update rating with a weighted average, considering previous rating
                self.rating = (self.rating * 4 + avg_rating) / 5
                self.save()

    def get_absolute_url(self):
        """Return the absolute URL of the skill."""
        return reverse("skill_detail", kwargs={"pk": self.pk})

    def deal_exists_for_user(self, user):
        """Check if a deal request exists for the current user and skill."""
        return SkillDeal.objects.filter(
            skill=self, provider=user, status=SkillDeal.PENDING
        ).exists()

    def user_has_rated(self, user):
        """Check if the logged in user has already rated this skill."""
        print("The code is checking if the logged in user has rated the skill.")
        return self.reviews.filter(owner=user).exists()

    def __str__(self):
        """Return a string representation of the skill."""
        return self.name


class SkillDeal(models.Model):
    """A model to represent a skill deal.

    Methods:
        mark_complete: Mark the skill deal as completed and set the end date.
        accept_deal: Accept the skill deal, set the start date, and set the status to active.

    Attributes:
        skill: A ForeignKey to represent the skill that is being dealt.
        owner: A ForeignKey to represent the user who owns the skill deal (the user requesting).
        provider: A ForeignKey to represent the user who owns the skill (the user who will provide).
        status: A CharField to represent the status of the skill deal.
        start_date: A DateTimeField to represent the date the skill deal was created.
        end_date: A DateTimeField to represent the date the skill deal was completed.
    """

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACTIVE, "Active"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner"
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requester"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def mark_complete(self) -> None:
        """Mark the skill deal as completed and set the end date."""
        self.status = self.COMPLETED
        self.end_date = timezone.now()
        self.save()

    def accept_deal(self) -> None:
        """Accept the skill deal, set the start date, and set the status to active."""
        self.status = self.ACTIVE
        self.start_date = timezone.now()
        self.save()

    def cancel_deal(self) -> None:
        """Cancel the skill deal and set the status to cancelled."""
        self.status = self.CANCELLED
        self.save()

    def is_owner(self, user):
        """Check if the user is the owner of the skill deal."""
        print("The code is checking if the logged in user owns the deal.")
        return self.owner == user

    def is_provider(self, user):
        """Check if the user is the provider of the skill deal."""
        print("The code is checking if the logged in user is the provider of the deal.")
        return self.provider == user

    def is_completed(self):
        """Check if the skill deal is completed."""
        print("The code is checking if the deal is completed.")
        return self.status == self.COMPLETED

    def send_message_on_request(self):
        """Send a message to the provider when a skill deal is requested."""
        Message.objects.create(
            sender=self.owner,
            receiver=self.provider,
            content=f"{self.owner.username} has requested a deal for {self.skill.name}",
        )

    def __str__(self):
        """Return a string representation of the skill deal."""
        return f"{self.skill} - Request by {self.owner} - Provided by {self.provider}"


class Message(models.Model):
    """A model to represent a message notification regarding a swap deal.

    Attributes:
        sender: A ForeignKey to represent the user who sent the message.
        receiver: A ForeignKey to represent the user who received the message.
        content: A TextField to represent the content of the message(optional).
        timestamp: A DateTimeField to represent the date the message was created.
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the message."""
        return f"Message from {self.sender.username} to {self.receiver.username}"


class Review(models.Model):
    """A model to represent the review and rating of a skill.

    Attributes:
        skill: A ForeignKey to represent the skill that is rated.
        owner: A ForeignKey to represent the user who is rating/reviewing the skill.
        review: A TextField to represent the review of the skill.
        rating: A float to represent the rating of the skill.
        date: A DateTimeField to represent the date the rating was created.

    """

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.FloatField(default=5.0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the rating."""
        return f"Review for {self.skill.name} - by {self.owner.username}"
