"""
Vues pour le système d'avis et notations
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils import timezone

from apps.accounts.models import ArtistProfile, OrganizerProfile, User
from .models import Review, ReviewRequest, ReviewResponse, ReviewHelpfulness
from .forms import ReviewForm, ReviewRequestForm, ReviewResponseForm, PublicReviewForm


@method_decorator(login_required, name="dispatch")
class LeaveReviewView(CreateView):
    """Vue pour laisser un avis sur un artiste"""

    model = Review
    form_class = ReviewForm
    template_name = "reviews/leave_review.html"
    success_url = reverse_lazy("reviews:my_reviews")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist_id = self.kwargs.get("artist_id")
        artist = get_object_or_404(ArtistProfile, id=artist_id)
        context["artist"] = artist
        context["page_title"] = f"Laisser un avis pour {artist.get_display_name()}"
        return context

    def form_valid(self, form):
        # Vérifier que l'utilisateur est un organisateur
        if not hasattr(self.request.user, "organizer_profile"):
            messages.error(
                self.request, "Seuls les organisateurs peuvent laisser des avis."
            )
            return redirect("accounts:profile")

        # Récupérer l'artiste
        artist_id = self.kwargs.get("artist_id")
        artist = get_object_or_404(ArtistProfile, id=artist_id)

        # Vérifier qu'il n'y a pas déjà un avis pour cet événement
        existing_review = Review.objects.filter(
            artist=artist,
            organizer=self.request.user.organizer_profile,
            event_date=form.cleaned_data.get("event_date"),
        ).first()

        if existing_review:
            messages.error(
                self.request, "Vous avez déjà laissé un avis pour cet événement."
            )
            return self.form_invalid(form)

        # Assigner l'artiste et l'organisateur
        form.instance.artist = artist
        form.instance.organizer = self.request.user.organizer_profile

        messages.success(self.request, "Votre avis a été publié avec succès !")
        return super().form_valid(form)


class PublicLeaveReviewView(CreateView):
    """Vue publique pour laisser un avis via token"""

    model = Review
    form_class = PublicReviewForm
    template_name = "reviews/public_leave_review.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get("token")

        try:
            review_request = get_object_or_404(ReviewRequest, token=token)

            # Vérifier que le lien n'est pas expiré
            if review_request.is_expired():
                context["expired"] = True
                return context

            # Vérifier que le lien n'a pas déjà été utilisé
            if review_request.is_used:
                context["already_used"] = True
                return context

            context["review_request"] = review_request
            context["artist"] = review_request.artist
            context["page_title"] = (
                f"Laisser un avis pour {review_request.artist.get_display_name()}"
            )

        except ReviewRequest.DoesNotExist:
            context["invalid_token"] = True

        return context

    def form_valid(self, form):
        token = self.kwargs.get("token")

        try:
            review_request = get_object_or_404(ReviewRequest, token=token)

            if review_request.is_expired() or review_request.is_used:
                messages.error(self.request, "Ce lien n'est plus valide.")
                return redirect("home")

            # Créer ou récupérer l'organisateur
            organizer_email = form.cleaned_data["organizer_email"]
            organizer_name = form.cleaned_data["organizer_name"]

            # Chercher si un utilisateur avec cet email existe
            user, created = User.objects.get_or_create(
                email=organizer_email,
                defaults={
                    "first_name": organizer_name.split()[0] if organizer_name else "",
                    "last_name": (
                        " ".join(organizer_name.split()[1:])
                        if len(organizer_name.split()) > 1
                        else ""
                    ),
                    "is_organizer": True,
                },
            )

            # Créer le profil organisateur si nécessaire
            organizer_profile, created = OrganizerProfile.objects.get_or_create(
                user=user, defaults={"company_name": organizer_name}
            )

            # Assigner les données à l'avis
            form.instance.artist = review_request.artist
            form.instance.organizer = organizer_profile
            form.instance.event_date = review_request.event_date
            form.instance.event_type = review_request.event_type
            form.instance.event_location = review_request.event_location

            # Marquer la demande comme utilisée
            review_request.is_used = True
            review_request.save()

            messages.success(
                self.request, "Merci ! Votre avis a été publié avec succès."
            )
            return super().form_valid(form)

        except ReviewRequest.DoesNotExist:
            messages.error(self.request, "Lien invalide.")
            return redirect("home")


@method_decorator(login_required, name="dispatch")
class RequestReviewView(CreateView):
    """Vue pour demander un avis à un client"""

    model = ReviewRequest
    form_class = ReviewRequestForm
    template_name = "reviews/request_review.html"
    success_url = reverse_lazy("reviews:my_reviews")

    def dispatch(self, request, *args, **kwargs):
        # Vérifier que l'utilisateur est un artiste
        if not hasattr(request.user, "artist_profile"):
            messages.error(request, "Seuls les artistes peuvent demander des avis.")
            return redirect("accounts:profile")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.artist = self.request.user.artist_profile
        messages.success(
            self.request, "Demande d'avis envoyée ! Un email sera envoyé au client."
        )
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class MyReviewsView(TemplateView):
    """Vue des avis de l'utilisateur"""

    template_name = "reviews/my_reviews.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if hasattr(user, "artist_profile"):
            # Avis reçus par l'artiste
            reviews_received = (
                Review.objects.filter(artist=user.artist_profile, is_public=True)
                .select_related("organizer", "organizer__user")
                .order_by("-created_at")
            )

            # Demandes d'avis envoyées
            review_requests = ReviewRequest.objects.filter(
                artist=user.artist_profile
            ).order_by("-created_at")

            context.update(
                {
                    "is_artist": True,
                    "reviews_received": reviews_received,
                    "review_requests": review_requests,
                    "average_rating": user.artist_profile.rating_average,
                    "total_reviews": reviews_received.count(),
                }
            )

        elif hasattr(user, "organizer_profile"):
            # Avis donnés par l'organisateur
            reviews_given = (
                Review.objects.filter(organizer=user.organizer_profile)
                .select_related("artist", "artist__user")
                .order_by("-created_at")
            )

            context.update(
                {
                    "is_organizer": True,
                    "reviews_given": reviews_given,
                }
            )

        context["page_title"] = "Mes avis"
        return context


@method_decorator(login_required, name="dispatch")
class RespondToReviewView(CreateView):
    """Vue pour répondre à un avis"""

    model = ReviewResponse
    form_class = ReviewResponseForm
    template_name = "reviews/respond.html"

    def get_success_url(self):
        return reverse("reviews:my_reviews")

    def dispatch(self, request, *args, **kwargs):
        # Vérifier que l'utilisateur est un artiste
        if not hasattr(request.user, "artist_profile"):
            messages.error(request, "Seuls les artistes peuvent répondre aux avis.")
            return redirect("accounts:profile")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_id = self.kwargs.get("pk")
        review = get_object_or_404(
            Review, id=review_id, artist=self.request.user.artist_profile
        )

        # Vérifier qu'il n'y a pas déjà une réponse
        if hasattr(review, "artist_response"):
            messages.info(self.request, "Vous avez déjà répondu à cet avis.")
            return redirect("reviews:my_reviews")

        context["review"] = review
        context["page_title"] = "Répondre à un avis"
        return context

    def form_valid(self, form):
        review_id = self.kwargs.get("pk")
        review = get_object_or_404(
            Review, id=review_id, artist=self.request.user.artist_profile
        )

        form.instance.review = review
        messages.success(self.request, "Votre réponse a été publiée avec succès !")
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class EditResponseView(UpdateView):
    """Vue pour éditer une réponse"""

    model = ReviewResponse
    form_class = ReviewResponseForm
    template_name = "reviews/edit_response.html"

    def get_success_url(self):
        return reverse("reviews:my_reviews")

    def get_queryset(self):
        # S'assurer que l'utilisateur ne peut éditer que ses propres réponses
        return ReviewResponse.objects.filter(
            review__artist=self.request.user.artist_profile
        )

    def form_valid(self, form):
        messages.success(self.request, "Votre réponse a été mise à jour avec succès !")
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
class MarkHelpfulView(TemplateView):
    """Vue pour marquer un avis comme utile"""

    def post(self, request, *args, **kwargs):
        review_id = kwargs.get("pk")
        review = get_object_or_404(Review, id=review_id)
        is_helpful = request.POST.get("is_helpful") == "true"

        # Créer ou mettre à jour le vote
        vote, created = ReviewHelpfulness.objects.get_or_create(
            review=review, user=request.user, defaults={"is_helpful": is_helpful}
        )

        if not created:
            vote.is_helpful = is_helpful
            vote.save()

        # Retourner les nouveaux comptes
        helpful_count = review.helpfulness_votes.filter(is_helpful=True).count()
        total_votes = review.helpfulness_votes.count()

        return JsonResponse(
            {
                "success": True,
                "helpful_count": helpful_count,
                "total_votes": total_votes,
                "user_voted_helpful": is_helpful,
            }
        )

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect("/")


class ArtistReviewsView(DetailView):
    """Vue publique des avis d'un artiste"""

    model = ArtistProfile
    template_name = "reviews/artist_reviews.html"
    context_object_name = "artist"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist = self.object

        # Récupérer les avis publics
        reviews = (
            Review.objects.filter(artist=artist, is_public=True)
            .select_related("organizer", "organizer__user")
            .prefetch_related("artist_response", "helpfulness_votes")
            .order_by("-created_at")
        )

        # Pagination
        paginator = Paginator(reviews, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # Statistiques
        stats = reviews.aggregate(
            total=Count("id"),
            average=Avg("rating"),
            rating_5=Count("id", filter=Q(rating=5)),
            rating_4=Count("id", filter=Q(rating=4)),
            rating_3=Count("id", filter=Q(rating=3)),
            rating_2=Count("id", filter=Q(rating=2)),
            rating_1=Count("id", filter=Q(rating=1)),
        )

        context.update(
            {
                "reviews": page_obj,
                "stats": stats,
                "page_title": f"Avis sur {artist.get_display_name()}",
            }
        )

        return context
