from django.urls import path
from .views import (
    SignupView,
    ProfileDecisionView,
    ProfileCreateView,
    ProfileUpdateView,
    ProfileView,
    CustomLoginView,
    CustomLogoutView,
    DashboardView,
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path(
        "profile/<int:user_id>/update",
        ProfileUpdateView.as_view(),
        name="profile_update",
    ),
    path("profile-decision/", ProfileDecisionView.as_view(), name="profile_decision"),
    path("profile/create/", ProfileCreateView.as_view(), name="profile_create"),
    path("profile/<int:user_id>/", ProfileView.as_view(), name="profile"),
    path("dashboard/<int:user_id>/", DashboardView.as_view(), name="dashboard"),
]
