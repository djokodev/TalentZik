"""
Vues pour les artistes et la recherche
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages

from apps.accounts.models import ArtistProfile
from .models import (
    MusicGenre,
    ArtistRole,
    Instrument,
    ProfileView,
    WhatsAppClick,
    SearchQuery,
)
from .forms import ArtistSearchForm, QuickSearchForm


class ArtistListView(ListView):
    """Liste des artistes avec pagination"""

    model = ArtistProfile
    template_name = "artists/list.html"
    context_object_name = "artists"
    paginate_by = 12

    def get_queryset(self):
        """Récupère tous les artistes triés par note"""
        return (
            ArtistProfile.objects.select_related("user")
            .prefetch_related("genres", "roles", "instruments")
            .order_by("-rating_average", "-total_reviews")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_title": "Tous les artistes",
                "page_description": "Découvrez tous les talents musicaux camerounais sur TalentZik",
                "total_artists": self.get_queryset().count(),
            }
        )
        return context


class ArtistSearchView(TemplateView):
    """Vue de recherche d'artistes avec filtres avancés"""

    template_name = "artists/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialiser le formulaire avec les données de la requête
        form = ArtistSearchForm(self.request.GET or None)

        # Récupérer tous les artistes de base
        queryset = ArtistProfile.objects.select_related("user").prefetch_related(
            "genres", "roles", "instruments"
        )

        # Appliquer les filtres si le formulaire est valide
        if form.is_valid():
            queryset = form.filter_queryset(queryset)

            # Enregistrer la recherche pour les statistiques
            search_query = form.cleaned_data.get("search")
            if search_query:
                SearchQuery.objects.create(
                    query=search_query,
                    user=(
                        self.request.user
                        if self.request.user.is_authenticated
                        else None
                    ),
                    results_count=queryset.count(),
                )

        # Assurer un ordering cohérent pour la pagination
        queryset = queryset.order_by("-rating_average", "-total_reviews", "id")

        # Pagination
        paginator = Paginator(queryset, 12)  # 12 artistes par page
        page = self.request.GET.get("page")

        try:
            artists = paginator.page(page)
        except PageNotAnInteger:
            artists = paginator.page(1)
        except EmptyPage:
            artists = paginator.page(paginator.num_pages)

        # Statistiques pour la sidebar
        stats = {
            "total_artists": ArtistProfile.objects.count(),
            "available_artists": ArtistProfile.objects.filter(
                is_available=True
            ).count(),
            "top_genres": MusicGenre.objects.annotate(artist_count=Count("artists"))
            .filter(artist_count__gt=0)
            .order_by("-artist_count")[:5],
            "regions_count": ArtistProfile.objects.values("region")
            .annotate(count=Count("id"))
            .order_by("-count")[:5],
        }

        context.update(
            {
                "form": form,
                "artists": artists,
                "stats": stats,
                "page_title": "Recherche d'artistes",
                "page_description": "Trouvez l'artiste parfait pour votre événement",
                "has_filters": (
                    any(form.cleaned_data.values()) if form.is_valid() else False
                ),
                "results_count": queryset.count() if form.is_valid() else 0,
            }
        )

        return context


class ArtistDetailView(DetailView):
    """Détail d'un artiste"""

    model = ArtistProfile
    template_name = "artists/detail.html"
    context_object_name = "artist"

    def get_object(self):
        """Récupère l'artiste et enregistre la vue"""
        artist = get_object_or_404(
            ArtistProfile.objects.select_related("user").prefetch_related(
                "genres", "roles", "instruments"
            ),
            pk=self.kwargs["pk"],
        )

        # Enregistrer la vue du profil (sauf si c'est l'artiste lui-même)
        if (
            self.request.user.is_authenticated
            and hasattr(self.request.user, "artist_profile")
            and self.request.user.artist_profile != artist
        ):
            ProfileView.objects.create(
                artist=artist, viewer=self.request.user, viewer_ip=self.get_client_ip()
            )
            # Incrémenter le compteur de vues
            artist.profile_views += 1
            artist.save(update_fields=["profile_views"])
        elif not self.request.user.is_authenticated:
            # Vue anonyme
            ProfileView.objects.create(artist=artist, viewer_ip=self.get_client_ip())
            artist.profile_views += 1
            artist.save(update_fields=["profile_views"])

        return artist

    def get_client_ip(self):
        """Récupère l'IP du client"""
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR")
        return ip

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist = self.object

        # Récupérer les fichiers multimédia
        audio_files = artist.audio_files.filter(is_active=True)[:3]
        video_files = artist.video_files.filter(is_active=True)[:2]
        photo_files = artist.photo_files.filter(is_active=True)[:6]
        documents = artist.documents.filter(is_active=True)[:3]

        # Récupérer les avis récents (à implémenter plus tard)
        # recent_reviews = artist.received_reviews.filter(is_public=True)[:5]

        # Artistes similaires (même genre ou même ville)
        similar_artists = (
            ArtistProfile.objects.filter(
                Q(genres__in=artist.genres.all()) | Q(city__iexact=artist.city)
            )
            .exclude(id=artist.id)
            .distinct()[:4]
        )

        context.update(
            {
                "page_title": f"Profil de {artist.get_display_name()}",
                "page_description": f"Découvrez le profil de {artist.get_display_name()}, artiste musical camerounais",
                "similar_artists": similar_artists,
                "audio_files": audio_files,
                "video_files": video_files,
                "photo_files": photo_files,
                "documents": documents,
                "can_contact": self.request.user.is_authenticated
                and hasattr(self.request.user, "organizer_profile"),
            }
        )

        return context


class ArtistContactView(TemplateView):
    """Vue de contact d'un artiste"""

    template_name = "artists/contact.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist = get_object_or_404(ArtistProfile, pk=self.kwargs["pk"])

        context.update(
            {
                "artist": artist,
                "page_title": f"Contacter {artist.get_display_name()}",
            }
        )

        return context


class WhatsAppRedirectView(TemplateView):
    """Redirection WhatsApp avec messages personnalisés"""

    template_name = "artists/whatsapp_contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist = get_object_or_404(ArtistProfile, pk=kwargs["pk"])

        # Templates de messages prédéfinis
        message_templates = [
            {
                "id": "general",
                "title": "Contact général",
                "message": f"Bonjour {artist.get_display_name()}, je vous contacte via TalentZik pour discuter d'une collaboration.",
                "icon": "fa-handshake",
            },
            {
                "id": "wedding",
                "title": "Mariage",
                "message": f"Bonjour {artist.get_display_name()}, je prépare un mariage et j'aimerais connaître vos disponibilités et tarifs.",
                "icon": "fa-ring",
            },
            {
                "id": "birthday",
                "title": "Anniversaire",
                "message": f"Bonjour {artist.get_display_name()}, j'organise un anniversaire et je recherche un artiste comme vous. Êtes-vous disponible ?",
                "icon": "fa-birthday-cake",
            },
            {
                "id": "corporate",
                "title": "Événement d'entreprise",
                "message": f"Bonjour {artist.get_display_name()}, notre entreprise organise un événement et nous recherchons un artiste professionnel. Pouvons-nous discuter ?",
                "icon": "fa-building",
            },
            {
                "id": "concert",
                "title": "Concert/Festival",
                "message": f"Bonjour {artist.get_display_name()}, nous organisons un concert/festival et aimerions vous proposer une participation. Intéressé(e) ?",
                "icon": "fa-music",
            },
            {
                "id": "custom",
                "title": "Message personnalisé",
                "message": "",
                "icon": "fa-edit",
            },
        ]

        context.update(
            {
                "artist": artist,
                "message_templates": message_templates,
                "page_title": f"Contacter {artist.get_display_name()} sur WhatsApp",
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        """Traiter la sélection du message et rediriger vers WhatsApp"""
        artist = get_object_or_404(ArtistProfile, pk=kwargs["pk"])
        message_type = request.POST.get("message_type", "general")
        custom_message = request.POST.get("custom_message", "")

        # Enregistrer le clic WhatsApp pour les statistiques
        WhatsAppClick.objects.create(
            artist=artist,
            clicker=request.user if request.user.is_authenticated else None,
            clicker_ip=self.get_client_ip(request),
        )

        # Déterminer le message à envoyer
        if message_type == "custom" and custom_message.strip():
            message = custom_message.strip()
        else:
            # Messages prédéfinis basés sur le type
            messages = {
                "general": f"Bonjour {artist.get_display_name()}, je vous contacte via TalentZik pour discuter d'une collaboration.",
                "wedding": f"Bonjour {artist.get_display_name()}, je prépare un mariage et j'aimerais connaître vos disponibilités et tarifs.",
                "birthday": f"Bonjour {artist.get_display_name()}, j'organise un anniversaire et je recherche un artiste comme vous. Êtes-vous disponible ?",
                "corporate": f"Bonjour {artist.get_display_name()}, notre entreprise organise un événement et nous recherchons un artiste professionnel. Pouvons-nous discuter ?",
                "concert": f"Bonjour {artist.get_display_name()}, nous organisons un concert/festival et aimerions vous proposer une participation. Intéressé(e) ?",
            }
            message = messages.get(message_type, messages["general"])

        # Rediriger vers WhatsApp
        whatsapp_number = artist.whatsapp_number or artist.phone_number
        if whatsapp_number:
            # Nettoyer le numéro (enlever espaces, tirets, etc.)
            clean_number = "".join(filter(str.isdigit, whatsapp_number))
            if not clean_number.startswith("237"):
                clean_number = "237" + clean_number.lstrip("0")

            # Encoder le message pour l'URL
            import urllib.parse

            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{clean_number}?text={encoded_message}"

            # Redirection directe si c'est une requête AJAX
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"redirect_url": whatsapp_url})

            return HttpResponseRedirect(whatsapp_url)

        # Si pas de numéro WhatsApp, rediriger vers la page de contact
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "Numéro WhatsApp non disponible"})

        messages.error(request, "Ce profil n'a pas de numéro WhatsApp configuré.")
        return redirect("artists:contact", pk=artist.pk)

    def get(self, request, *args, **kwargs):
        """Afficher l'interface de sélection du message ou redirection directe"""
        # Si paramètre 'direct' dans l'URL, redirection immédiate
        if request.GET.get("direct") == "true":
            return self.post(request, *args, **kwargs)

        # Sinon, afficher l'interface de sélection
        return super().get(request, *args, **kwargs)

    def get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


# API Views pour les données JSON (pour futurs développements)


class GenreListAPIView(TemplateView):
    """API des genres musicaux"""

    def get(self, request, *args, **kwargs):
        """Retourne la liste des genres avec le nombre d'artistes"""
        genres = (
            MusicGenre.objects.filter(is_active=True)
            .annotate(artist_count=Count("artists"))
            .order_by("name")
            .values("id", "name", "artist_count")
        )
        return JsonResponse({"genres": list(genres)})


class RoleListAPIView(TemplateView):
    """API des rôles d'artistes"""

    def get(self, request, *args, **kwargs):
        """Retourne la liste des rôles avec le nombre d'artistes"""
        roles = (
            ArtistRole.objects.all()
            .annotate(artist_count=Count("artists"))
            .order_by("name")
            .values("id", "name", "artist_count")
        )
        return JsonResponse({"roles": list(roles)})


class InstrumentListAPIView(TemplateView):
    """API des instruments"""

    def get(self, request, *args, **kwargs):
        """Retourne la liste des instruments avec le nombre d'artistes"""
        instruments = (
            Instrument.objects.filter(is_active=True)
            .annotate(artist_count=Count("artists"))
            .order_by("name")
            .values("id", "name", "artist_count")
        )
        return JsonResponse({"instruments": list(instruments)})


class QuickSearchAPIView(TemplateView):
    """API de recherche rapide pour l'autocomplétion"""

    def get(self, request, *args, **kwargs):
        form = QuickSearchForm(request.GET)
        results = []

        if form.is_valid() and form.cleaned_data["q"]:
            query = form.cleaned_data["q"]

            # Rechercher dans les artistes
            artists = ArtistProfile.objects.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(stage_name__icontains=query)
            ).select_related("user")[:5]

            for artist in artists:
                results.append(
                    {
                        "type": "artist",
                        "id": artist.id,
                        "name": artist.display_name,
                        "subtitle": f"{artist.city}, {artist.region}",
                        "url": f"/artists/{artist.id}/",
                        "avatar": (
                            artist.profile_picture.url
                            if artist.profile_picture
                            else None
                        ),
                    }
                )

        return JsonResponse({"results": results})


class WhatsAppStatsView(TemplateView):
    """Statistiques WhatsApp pour les artistes"""

    template_name = "artists/whatsapp_stats.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # Vérifier que l'utilisateur est un artiste
        if not hasattr(request.user, "artist_profile"):
            messages.error(
                request, "Seuls les artistes peuvent accéder à ces statistiques."
            )
            return redirect("accounts:profile")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist = self.request.user.artist_profile

        # Statistiques globales
        total_clicks = artist.whatsapp_clicks.count()

        # Statistiques par période (30 derniers jours)
        from datetime import datetime, timedelta
        from django.utils import timezone

        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_clicks = artist.whatsapp_clicks.filter(clicked_at__gte=thirty_days_ago)

        # Clics par jour (7 derniers jours)
        seven_days_ago = timezone.now() - timedelta(days=7)
        daily_clicks = {}
        for i in range(7):
            day = seven_days_ago + timedelta(days=i)
            day_key = day.strftime("%Y-%m-%d")
            daily_clicks[day_key] = artist.whatsapp_clicks.filter(
                clicked_at__date=day.date()
            ).count()

        # Top utilisateurs qui ont cliqué
        from django.db.models import Count

        top_clickers = (
            artist.whatsapp_clicks.exclude(clicker=None)
            .values("clicker__first_name", "clicker__last_name", "clicker__email")
            .annotate(click_count=Count("id"))
            .order_by("-click_count")[:5]
        )

        # Clics anonymes
        anonymous_clicks = artist.whatsapp_clicks.filter(clicker=None).count()

        # Pourcentage de conversion (clics vs vues de profil)
        if artist.profile_views > 0:
            conversion_rate = (total_clicks / artist.profile_views) * 100
        else:
            conversion_rate = 0

        context.update(
            {
                "artist": artist,
                "total_clicks": total_clicks,
                "recent_clicks_count": recent_clicks.count(),
                "daily_clicks": daily_clicks,
                "top_clickers": top_clickers,
                "anonymous_clicks": anonymous_clicks,
                "conversion_rate": round(conversion_rate, 1),
                "page_title": "Statistiques WhatsApp",
            }
        )

        return context
