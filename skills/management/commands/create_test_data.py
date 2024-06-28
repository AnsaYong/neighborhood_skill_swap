"""A script to create test data for the project."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import UserProfile
from skills.models import Category, Skill, Review, SkillDeal
import random


class Command(BaseCommand):
    """A class to create test data for the project."""

    help = "Create test users with profiles, skills, reviews, and skill deals"

    def handle(self, *args, **kwargs):
        """Create test data for the project."""
        User = get_user_model()

        # Create test users
        users = []
        for i in range(1, 6):
            user = User.objects.create_user(
                username=f"testuser{i}", password="password123", age=20 + i
            )
            users.append(user)
            # Create user profiles
            UserProfile.objects.create(
                user=user,
                location=f"City {i}",
                bio=f"Test bio for test user {i}",
                credits=i * 100,
            )

        # Create categories
        categories = []
        for i in range(1, 6):
            category = Category.objects.create(name=f"Category {i}")
            categories.append(category)

        # Create skills for each user
        skills = []
        skill_names = [
            "Python Programming",
            "Web Development",
            "Data Science",
            "Italian Cooking",
            "French Cooking",
            "Guitar Playing",
            "Graphic Design",
            "Digital Marketing",
            "Public Speaking",
            "Project Management",
            "Yoga Instruction",
            "Fitness Training",
            "Photography",
            "Video Editing",
            "Content Writing",
        ]

        for user in users:
            offered_skills = random.sample(skill_names, 3)
            wanted_skills = random.sample(skill_names, 3)
            for skill_name in offered_skills:
                skill = Skill.objects.create(
                    name=skill_name,
                    category=random.choice(categories),
                    level="Intermediate",
                    description=f"{skill_name} skills offered.",
                    owner=user,
                    skill_type="offered",
                )
                skills.append(skill)
            for skill_name in wanted_skills:
                skill = Skill.objects.create(
                    name=skill_name,
                    category=random.choice(categories),
                    level="Intermediate",
                    description=f"{skill_name} skills wanted.",
                    owner=user,
                    skill_type="wanted",
                )
                skills.append(skill)

        # Create reviews
        for i in range(15):
            Review.objects.create(
                skill=skills[i],
                owner=users[(i + 1) % 5],  # The next user reviews the skill
                review=f"Great {skills[i].name} skills!",
                rating=4.0 + i % 2,  # Alternate ratings between 4.0 and 5.0
            )

        # Create skill deals
        start_date = timezone.now()
        for i in range(15):
            end_date = start_date + timezone.timedelta(
                hours=2 * (i + 1)
            )  # Different durations
            deal = SkillDeal.objects.create(
                skill=skills[i],
                owner=users[(i + 1) % 5],  # The next user requests the skill
                provider=users[i % 5],  # The user owns the skill
                status=SkillDeal.COMPLETED,
                start_date=start_date,
                end_date=end_date,
            )
            # Update credits for skill deals
            deal.save()

        self.stdout.write(
            self.style.SUCCESS("Successfully created test data with 5 users")
        )
