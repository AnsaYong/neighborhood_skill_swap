# Generated by Django 5.0.6 on 2024-06-26 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("skills", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="skill",
            name="skill_type",
            field=models.CharField(default="offered", max_length=20),
            preserve_default=False,
        ),
    ]
