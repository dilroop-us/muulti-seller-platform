from django.urls import path, include
from .views import profile_view, edit_profile, payment_history

app_name = "customer"

urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("history/", payment_history, name="payment_history"),
]
