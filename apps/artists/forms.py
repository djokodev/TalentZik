"""
Formulaires pour la recherche et les filtres d'artistes
"""

from django import forms
from django.db.models import Q

from apps.accounts.models import ArtistProfile
from .models import MusicGenre, ArtistRole, Instrument


class ArtistSearchForm(forms.Form):
    """
    Formulaire de recherche d'artistes avec filtres avancés
    """

    # Recherche textuelle
    search = forms.CharField(
        label="Rechercher un artiste",
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Nom d'artiste, nom de scène, ville...",
                "autocomplete": "off",
            }
        ),
        help_text="Recherchez par nom, nom de scène, ville ou région",
    )

    # Filtres par localisation camerounaise
    CAMEROON_REGIONS = [
        ("", "Toutes les régions"),
        ("adamaoua", "Adamaoua"),
        ("centre", "Centre"),
        ("est", "Est"),
        ("extreme-nord", "Extrême-Nord"),
        ("littoral", "Littoral"),
        ("nord", "Nord"),
        ("nord-ouest", "Nord-Ouest"),
        ("ouest", "Ouest"),
        ("sud", "Sud"),
        ("sud-ouest", "Sud-Ouest"),
    ]

    region = forms.ChoiceField(
        label="Région",
        choices=CAMEROON_REGIONS,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            }
        ),
    )

    # Grandes villes camerounaises
    MAJOR_CITIES = [
        ("", "Toutes les villes"),
        ("douala", "Douala"),
        ("yaounde", "Yaoundé"),
        ("bamenda", "Bamenda"),
        ("bafoussam", "Bafoussam"),
        ("garoua", "Garoua"),
        ("maroua", "Maroua"),
        ("ngaoundere", "Ngaoundéré"),
        ("bertoua", "Bertoua"),
        ("buea", "Buea"),
        ("limbe", "Limbé"),
        ("edea", "Edéa"),
        ("kumba", "Kumba"),
        ("foumban", "Foumban"),
        ("dschang", "Dschang"),
        ("ebolowa", "Ebolowa"),
        ("sangmelima", "Sangmélima"),
    ]

    city = forms.ChoiceField(
        label="Ville",
        choices=MAJOR_CITIES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            }
        ),
    )

    # Filtres musicaux
    genres = forms.ModelMultipleChoiceField(
        label="Genres musicaux",
        queryset=MusicGenre.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "data-toggle": "multiselect",
                "multiple": "multiple",
            }
        ),
    )

    roles = forms.ModelMultipleChoiceField(
        label="Rôles artistiques",
        queryset=ArtistRole.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "grid grid-cols-2 gap-2",
            }
        ),
    )

    instruments = forms.ModelMultipleChoiceField(
        label="Instruments",
        queryset=Instrument.objects.filter(is_active=True).order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "grid grid-cols-2 gap-2",
            }
        ),
    )

    # Filtres de disponibilité
    is_available = forms.BooleanField(
        label="Seulement les artistes disponibles",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded",
            }
        ),
    )

    # Filtres par note
    RATING_CHOICES = [
        ("", "Toutes les notes"),
        ("4", "4 étoiles et plus"),
        ("3", "3 étoiles et plus"),
        ("2", "2 étoiles et plus"),
        ("1", "1 étoile et plus"),
    ]

    min_rating = forms.ChoiceField(
        label="Note minimum",
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            }
        ),
    )

    # Tri des résultats
    SORT_CHOICES = [
        ("name", "Nom (A-Z)"),
        ("-name", "Nom (Z-A)"),
        ("-rating_average", "Mieux notés"),
        ("-total_reviews", "Plus d'avis"),
        ("-profile_views", "Plus populaires"),
        ("-created_at", "Plus récents"),
        ("created_at", "Plus anciens"),
    ]

    sort_by = forms.ChoiceField(
        label="Trier par",
        choices=SORT_CHOICES,
        required=False,
        initial="-rating_average",
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mettre à jour les choix de genres, rôles et instruments depuis la base de données
        self.fields["genres"].queryset = MusicGenre.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["roles"].queryset = ArtistRole.objects.filter(
            is_active=True
        ).order_by("name")
        self.fields["instruments"].queryset = Instrument.objects.filter(
            is_active=True
        ).order_by("name")

    def filter_queryset(self, queryset):
        """
        Applique les filtres au queryset d'artistes
        """
        if not self.is_valid():
            return queryset

        data = self.cleaned_data

        # Recherche textuelle
        if data.get("search"):
            search_query = data["search"]
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query)
                | Q(user__last_name__icontains=search_query)
                | Q(stage_name__icontains=search_query)
                | Q(city__icontains=search_query)
                | Q(region__icontains=search_query)
                | Q(bio__icontains=search_query)
            )

        # Filtres géographiques
        if data.get("region"):
            queryset = queryset.filter(region__icontains=data["region"])

        if data.get("city"):
            queryset = queryset.filter(city__icontains=data["city"])

        # Filtres musicaux
        if data.get("genres"):
            queryset = queryset.filter(genres__in=data["genres"]).distinct()

        if data.get("roles"):
            queryset = queryset.filter(roles__in=data["roles"]).distinct()

        if data.get("instruments"):
            queryset = queryset.filter(instruments__in=data["instruments"]).distinct()

        # Filtre de disponibilité
        if data.get("is_available"):
            queryset = queryset.filter(is_available=True)

        # Filtre par note minimum
        if data.get("min_rating"):
            min_rating = float(data["min_rating"])
            queryset = queryset.filter(rating_average__gte=min_rating)

        # Tri
        sort_by = data.get("sort_by", "-rating_average")
        if sort_by == "name":
            # Tri par nom : utiliser le stage_name en priorité, sinon le nom complet
            queryset = queryset.extra(
                select={
                    "display_name": 'CASE WHEN stage_name != "" THEN stage_name ELSE CONCAT(accounts_user.first_name, " ", accounts_user.last_name) END'
                }
            ).order_by("display_name")
        elif sort_by == "-name":
            queryset = queryset.extra(
                select={
                    "display_name": 'CASE WHEN stage_name != "" THEN stage_name ELSE CONCAT(accounts_user.first_name, " ", accounts_user.last_name) END'
                }
            ).order_by("-display_name")
        else:
            queryset = queryset.order_by(sort_by)

        return queryset


class QuickSearchForm(forms.Form):
    """
    Formulaire de recherche rapide pour la barre de navigation
    """

    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "Rechercher un artiste...",
                "autocomplete": "off",
            }
        ),
    )
