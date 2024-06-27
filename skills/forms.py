from django import forms

from .models import Skill, Category, SkillDeal


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


class SkillDealForm(forms.ModelForm):
    """A form to create and update skill deal details.

    Attributes:
        class Meta: A class to represent the model and manipulate fields of the form.
    """

    class Meta:
        """Additional settings - Set the model and fields of the form.

        Attributes:
            model: A model to represent the model of the form.
            fields: A list to represent the fields of the form.
            widgets: Fields to hide when the form is rendered.
        """

        model = SkillDeal
        fields = ["skill", "owner", "provider", "status", "start_date", "end_date"]
        widgets = {
            "skill": forms.HiddenInput(),
            "owner": forms.HiddenInput(),
            "provider": forms.HiddenInput(),
            "status": forms.HiddenInput(),
        }


class SkillDealAcceptForm(forms.ModelForm):
    """A form to accept a skill deal.

    Attributes:
        class Meta: A class to represent the model and manipulate fields of the form.
    """

    class Meta:
        """Additional settings - Set the model and fields of the form.

        Attributes:
            model: A model to represent the model of the form.
            fields: A list to represent the fields of the form.
            widgets: Fields to hide when the form is rendered.
        """

        model = SkillDeal
        fields = ["status", "start_date"]
        widgets = {
            "status": forms.HiddenInput(),
            "start_date": forms.HiddenInput(),
        }
