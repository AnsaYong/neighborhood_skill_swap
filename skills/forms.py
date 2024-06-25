from django import forms

from .models import Skill, Category


class SkillForm(forms.ModelForm):
    """A form to accept skill details.

    Attributes:
        class Meta: A class to represent the model and fields of the form.
    """

    class Meta:
        model = Skill
        fields = ["name", "Level", "description", "category"]

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), empty_label="Select a category"
    )


class SkillSearchForm(forms.Form):
    """A form to accept search term.

    Attributes:
        search: A CharField to represent the search field.
    """

    search_term = forms.CharField(max_length=100, required=False, label="Search")
