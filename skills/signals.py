"""This module contains the signals for the skill deal app.
It updates the skill provider's credits once they have completed a skill deal"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from skills.models import SkillDeal


@receiver(post_save, sender=SkillDeal)
def update_provider_credits(sender, instance, **kwargs) -> None:
    """Update credits in the UserProfile of both the
    skill provider (add) and the user who requested the skill (subtract)
    once the skill deal is completed.


    Args:
        sender: The sender of the signal - the class object.
        instance: The instance of the signal.
        **kwargs: Additional keyword arguments.
    """

    if instance.status == SkillDeal.COMPLETED and instance.end_date is not None:
        time_spent = instance.end_date - instance.start_date  # format: timedelta
        credits_to_add = int(
            time_spent.total_seconds() * 0.02778
        )  # 100 credits per hour

        instance.provider.profile.credits += credits_to_add
        instance.provider.profile.save()

        instance.owner.profile.credits -= credits_to_add
        instance.owner.profile.save()
