"""
URLs pour l'application artists (recherche et profils d'artistes)
"""

from django.urls import path
from . import views

app_name = "artists"

urlpatterns = [
    # Recherche et listing
    path("", views.ArtistListView.as_view(), name="list"),
    path("search/", views.ArtistSearchView.as_view(), name="search"),
    # Profils d'artistes
    path("<int:pk>/", views.ArtistDetailView.as_view(), name="detail"),
    path("<int:pk>/contact/", views.ArtistContactView.as_view(), name="contact"),
    path("<int:pk>/whatsapp/", views.WhatsAppRedirectView.as_view(), name="whatsapp"),
    path("whatsapp/stats/", views.WhatsAppStatsView.as_view(), name="whatsapp_stats"),
    # API pour les filtres et recherche
    path("api/genres/", views.GenreListAPIView.as_view(), name="api_genres"),
    path("api/roles/", views.RoleListAPIView.as_view(), name="api_roles"),
    path(
        "api/instruments/",
        views.InstrumentListAPIView.as_view(),
        name="api_instruments",
    ),
    path(
        "api/quick-search/", views.QuickSearchAPIView.as_view(), name="api_quick_search"
    ),
]
