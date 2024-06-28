from django.views.generic import TemplateView


# Create your views here.
class LandingPageView(TemplateView):
    """Landing page view."""

    template_name = "landing.html"
