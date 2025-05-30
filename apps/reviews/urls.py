"""
URLs pour l'application reviews (système d'avis et notations)
"""

from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    # Gestion des avis
    path("leave/<uuid:token>/", views.LeaveReviewView.as_view(), name="leave_review"),
    path("request/", views.RequestReviewView.as_view(), name="request_review"),
    path("my-reviews/", views.MyReviewsView.as_view(), name="my_reviews"),
    # Réponses aux avis
    path("<int:pk>/respond/", views.RespondToReviewView.as_view(), name="respond"),
    path(
        "response/<int:pk>/edit/",
        views.EditResponseView.as_view(),
        name="edit_response",
    ),
    # Votes d'utilité
    path("<int:pk>/helpful/", views.MarkHelpfulView.as_view(), name="mark_helpful"),
]
