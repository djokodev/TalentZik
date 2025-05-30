"""
Modèles pour le système de notation et d'avis des artistes
"""

import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


class Review(models.Model):
    """
    Avis et notations des artistes par les organisateurs
    """

    EVENT_TYPE_CHOICES = [
        ("wedding_traditional", _("Mariage traditionnel")),
        ("wedding_civil", _("Mariage civil")),
        ("wedding_religious", _("Mariage religieux")),
        ("dowry", _("Dot/Libation")),
        ("funeral", _("Funérailles/Deuil")),
        ("baptism", _("Baptême")),
        ("mass", _("Messe/Service religieux")),
        ("prayer_vigil", _("Veillée de prière")),
        ("evangelization", _("Croisade d'évangélisation")),
        ("gospel_concert", _("Concert gospel")),
        ("spiritual_retreat", _("Retraite spirituelle")),
        ("pilgrimage", _("Pèlerinage")),
        ("birthday", _("Anniversaire")),
        ("engagement", _("Fiançailles")),
        ("baby_shower", _("Baby shower")),
        ("new_year", _("Fête de fin d'année")),
        ("new_year_eve", _("Réveillon")),
        ("dance_party", _("Soirée dansante")),
        ("company_party", _("Fête d'entreprise")),
        ("corporate_event", _("Événement d'entreprise")),
        ("product_launch", _("Lancement de produit")),
        ("seminar", _("Séminaire/Conférence")),
        ("charity_gala", _("Gala de charité")),
        ("political_event", _("Événement politique")),
        ("national_day", _("Fête nationale (20 mai)")),
        ("youth_day", _("Fête de la jeunesse (11 février)")),
        ("public_concert", _("Concert public")),
        ("music_festival", _("Festival de musique")),
        ("other", _("Autre")),
    ]

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Artiste"),
    )
    organizer = models.ForeignKey(
        "accounts.OrganizerProfile",
        on_delete=models.CASCADE,
        related_name="given_reviews",
        verbose_name=_("Organisateur"),
    )
    rating = models.PositiveIntegerField(
        _("Note"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Note de 1 à 5 étoiles"),
    )
    comment = models.TextField(
        _("Commentaire"),
        blank=True,
        help_text=_("Commentaire détaillé sur la prestation (optionnel)"),
    )
    event_date = models.DateField(
        _("Date de l'événement"),
        null=True,
        blank=True,
        help_text=_("Date à laquelle la prestation a eu lieu"),
    )
    event_type = models.CharField(
        _("Type d'événement"),
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        blank=True,
        help_text=_("Type d'événement pour lequel l'artiste a été engagé"),
    )
    event_location = models.CharField(
        _("Lieu de l'événement"),
        max_length=200,
        blank=True,
        help_text=_("Ville ou lieu où s'est déroulé l'événement"),
    )
    is_verified = models.BooleanField(
        _("Avis vérifié"),
        default=False,
        help_text=_("Indique si l'avis a été vérifié par l'équipe"),
    )
    is_public = models.BooleanField(
        _("Avis public"),
        default=True,
        help_text=_("Indique si l'avis est visible publiquement"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)

    class Meta:
        verbose_name = _("Avis")
        verbose_name_plural = _("Avis")
        db_table = "reviews_review"
        unique_together = ["artist", "organizer", "event_date"]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["artist", "is_public"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_verified"]),
        ]

    def __str__(self):
        return f"Avis de {self.organizer.get_display_name()} pour {self.artist.get_display_name()} - {self.rating}★"

    def get_rating_stars(self):
        """
        Retourne une représentation visuelle de la note en étoiles
        """
        return "★" * self.rating + "☆" * (5 - self.rating)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour la note moyenne de l'artiste
        self.artist.update_rating_average()


class ReviewRequest(models.Model):
    """
    Demandes d'avis envoyées par les artistes à leurs clients
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="review_requests",
        verbose_name=_("Artiste"),
    )
    client_email = models.EmailField(
        _("Email du client"),
        help_text=_("Adresse email du client pour recevoir la demande d'avis"),
    )
    client_name = models.CharField(
        _("Nom du client"),
        max_length=200,
        blank=True,
        help_text=_("Nom du client (optionnel)"),
    )
    client_phone = models.CharField(
        _("Téléphone du client"),
        max_length=20,
        blank=True,
        help_text=_("Numéro de téléphone du client (optionnel)"),
    )
    event_date = models.DateField(
        _("Date de l'événement"), help_text=_("Date de la prestation")
    )
    event_type = models.CharField(
        _("Type d'événement"),
        max_length=30,
        choices=Review.EVENT_TYPE_CHOICES,
        help_text=_("Type d'événement"),
    )
    event_location = models.CharField(
        _("Lieu de l'événement"),
        max_length=200,
        blank=True,
        help_text=_("Lieu où s'est déroulé l'événement"),
    )
    token = models.UUIDField(
        _("Token"),
        default=uuid.uuid4,
        unique=True,
        help_text=_("Token unique pour le lien d'avis"),
    )
    message = models.TextField(
        _("Message personnalisé"),
        blank=True,
        help_text=_("Message personnalisé à inclure dans l'email"),
    )
    is_sent = models.BooleanField(
        _("Email envoyé"), default=False, help_text=_("Indique si l'email a été envoyé")
    )
    is_used = models.BooleanField(
        _("Lien utilisé"),
        default=False,
        help_text=_("Indique si le client a utilisé le lien pour laisser un avis"),
    )
    sent_at = models.DateTimeField(_("Envoyé le"), null=True, blank=True)
    expires_at = models.DateTimeField(
        _("Expire le"), help_text=_("Date d'expiration du lien")
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Demande d'Avis")
        verbose_name_plural = _("Demandes d'Avis")
        db_table = "reviews_review_request"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["artist"]),
            models.Index(fields=["token"]),
            models.Index(fields=["is_used"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Demande d'avis de {self.artist.get_display_name()} pour {self.client_email}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Le lien expire après 30 jours par défaut
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_expired(self):
        """
        Vérifie si la demande d'avis a expiré
        """
        return timezone.now() > self.expires_at

    def is_valid(self):
        """
        Vérifie si la demande d'avis est valide (non utilisée et non expirée)
        """
        return not self.is_used and not self.is_expired()

    def get_review_url(self):
        """
        Génère l'URL pour laisser un avis
        """
        from django.urls import reverse

        return reverse("reviews:leave_review", kwargs={"token": self.token})


class ReviewResponse(models.Model):
    """
    Réponses des artistes aux avis reçus
    """

    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name="artist_response",
        verbose_name=_("Avis"),
    )
    response_text = models.TextField(
        _("Réponse"), help_text=_("Réponse de l'artiste à l'avis")
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)

    class Meta:
        verbose_name = _("Réponse à un Avis")
        verbose_name_plural = _("Réponses aux Avis")
        db_table = "reviews_review_response"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Réponse de {self.review.artist.get_display_name()} à l'avis de {self.review.organizer.get_display_name()}"


class ReviewHelpfulness(models.Model):
    """
    Votes d'utilité des avis par les utilisateurs
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="helpfulness_votes",
        verbose_name=_("Avis"),
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="review_votes",
        verbose_name=_("Utilisateur"),
    )
    is_helpful = models.BooleanField(
        _("Utile"), help_text=_("Indique si l'utilisateur trouve l'avis utile")
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Vote d'Utilité")
        verbose_name_plural = _("Votes d'Utilité")
        db_table = "reviews_review_helpfulness"
        unique_together = ["review", "user"]
        indexes = [
            models.Index(fields=["review"]),
            models.Index(fields=["is_helpful"]),
        ]

    def __str__(self):
        helpful_text = "utile" if self.is_helpful else "pas utile"
        return f"{self.user.get_full_name()} trouve l'avis {helpful_text}"


class ReviewStatistics(models.Model):
    """
    Statistiques des avis pour chaque artiste (mise à jour périodique)
    """

    artist = models.OneToOneField(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="review_stats",
        verbose_name=_("Artiste"),
    )
    total_reviews = models.PositiveIntegerField(_("Total des avis"), default=0)
    average_rating = models.DecimalField(
        _("Note moyenne"), max_digits=3, decimal_places=2, default=0.00
    )
    rating_1_count = models.PositiveIntegerField(_("Avis 1 étoile"), default=0)
    rating_2_count = models.PositiveIntegerField(_("Avis 2 étoiles"), default=0)
    rating_3_count = models.PositiveIntegerField(_("Avis 3 étoiles"), default=0)
    rating_4_count = models.PositiveIntegerField(_("Avis 4 étoiles"), default=0)
    rating_5_count = models.PositiveIntegerField(_("Avis 5 étoiles"), default=0)
    last_review_date = models.DateTimeField(_("Dernier avis"), null=True, blank=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Statistiques d'Avis")
        verbose_name_plural = _("Statistiques d'Avis")
        db_table = "reviews_review_statistics"

    def __str__(self):
        return f"Stats de {self.artist.get_display_name()} - {self.average_rating}★ ({self.total_reviews} avis)"

    def update_statistics(self):
        """
        Met à jour les statistiques basées sur les avis publics
        """
        reviews = Review.objects.filter(artist=self.artist, is_public=True)

        self.total_reviews = reviews.count()

        if self.total_reviews > 0:
            # Calcul de la moyenne
            total_rating = sum(review.rating for review in reviews)
            self.average_rating = total_rating / self.total_reviews

            # Comptage par note
            self.rating_1_count = reviews.filter(rating=1).count()
            self.rating_2_count = reviews.filter(rating=2).count()
            self.rating_3_count = reviews.filter(rating=3).count()
            self.rating_4_count = reviews.filter(rating=4).count()
            self.rating_5_count = reviews.filter(rating=5).count()

            # Dernier avis
            last_review = reviews.order_by("-created_at").first()
            self.last_review_date = last_review.created_at if last_review else None
        else:
            self.average_rating = 0.00
            self.rating_1_count = 0
            self.rating_2_count = 0
            self.rating_3_count = 0
            self.rating_4_count = 0
            self.rating_5_count = 0
            self.last_review_date = None

        self.save()

    def get_rating_distribution(self):
        """
        Retourne la distribution des notes en pourcentages
        """
        if self.total_reviews == 0:
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        return {
            1: round((self.rating_1_count / self.total_reviews) * 100, 1),
            2: round((self.rating_2_count / self.total_reviews) * 100, 1),
            3: round((self.rating_3_count / self.total_reviews) * 100, 1),
            4: round((self.rating_4_count / self.total_reviews) * 100, 1),
            5: round((self.rating_5_count / self.total_reviews) * 100, 1),
        }
