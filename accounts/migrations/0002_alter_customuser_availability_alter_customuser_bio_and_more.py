# Generated by Django 5.0.6 on 2024-06-21 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="availability",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="bio",
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="location",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="phone_number",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="skills_offered",
            field=models.TextField(blank=True, max_length=500),
        ),
    ]
