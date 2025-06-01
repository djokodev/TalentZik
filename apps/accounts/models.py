"""
Modèles pour l'authentification et les profils utilisateurs
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur personnalisé utilisant l'email comme identifiant unique
    """

    USER_TYPE_CHOICES = [
        ("artist", _("Artiste")),
        ("organizer", _("Organisateur")),
    ]

    email = models.EmailField(
        _("Adresse email"),
        unique=True,
        help_text=_("Adresse email utilisée pour la connexion"),
    )
    first_name = models.CharField(_("Prénom"), max_length=150, blank=True)
    last_name = models.CharField(_("Nom"), max_length=150, blank=True)
    user_type = models.CharField(
        _("Type d'utilisateur"),
        max_length=20,
        choices=USER_TYPE_CHOICES,
        help_text=_("Définit si l'utilisateur est un artiste ou un organisateur"),
    )
    is_staff = models.BooleanField(
        _("Statut équipe"),
        default=False,
        help_text=_("Détermine si l'utilisateur peut se connecter à l'admin"),
    )
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
        help_text=_(
            "Détermine si ce compte utilisateur doit être considéré comme actif"
        ),
    )
    email_verified = models.BooleanField(
        _("Email vérifié"),
        default=False,
        help_text=_("Indique si l'adresse email a été vérifiée"),
    )
    date_joined = models.DateTimeField(_("Date d'inscription"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "user_type"]

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        db_table = "accounts_user"

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Retourne le prénom et le nom, avec un espace entre les deux
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """
        Retourne le prénom de l'utilisateur
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Envoie un email à cet utilisateur
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_artist(self):
        """Vérifie si l'utilisateur est un artiste"""
        return self.user_type == "artist"

    @property
    def is_organizer(self):
        """Vérifie si l'utilisateur est un organisateur"""
        return self.user_type == "organizer"


class ArtistProfile(models.Model):
    """
    Profil détaillé pour les artistes musicaux
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="artist_profile",
        verbose_name=_("Utilisateur"),
    )
    stage_name = models.CharField(
        _("Nom de scène"),
        max_length=100,
        blank=True,
        help_text=_("Nom artistique ou nom de scène (optionnel)"),
    )
    phone_number = models.CharField(
        _("Numéro de téléphone"),
        max_length=20,
        help_text=_("Numéro de téléphone principal"),
    )
    whatsapp_number = models.CharField(
        _("Numéro WhatsApp"),
        max_length=20,
        blank=True,
        help_text=_("Numéro WhatsApp pour contact direct"),
    )
    bio = models.TextField(
        _("Biographie"),
        blank=True,
        help_text=_("Description de votre parcours et style musical"),
    )
    profile_picture = models.ImageField(
        _("Photo de profil"), upload_to="profiles/artists/", blank=True, null=True
    )
    city = models.CharField(
        _("Ville"), max_length=100, help_text=_("Ville de résidence")
    )
    region = models.CharField(
        _("Région"), max_length=100, help_text=_("Région du Cameroun")
    )
    is_available = models.BooleanField(
        _("Disponible"),
        default=True,
        help_text=_("Indique si l'artiste est disponible pour de nouveaux contrats"),
    )
    rating_average = models.DecimalField(
        _("Note moyenne"),
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text=_("Note moyenne calculée automatiquement"),
    )
    total_reviews = models.PositiveIntegerField(
        _("Nombre total d'avis"), default=0, help_text=_("Nombre total d'avis reçus")
    )
    profile_views = models.PositiveIntegerField(
        _("Vues du profil"),
        default=0,
        help_text=_("Nombre de fois que le profil a été consulté"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)

    class Meta:
        verbose_name = _("Profil Artiste")
        verbose_name_plural = _("Profils Artistes")
        db_table = "accounts_artist_profile"
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["region"]),
            models.Index(fields=["is_available"]),
            models.Index(fields=["rating_average"]),
        ]

    def __str__(self):
        return self.get_display_name()

    def get_display_name(self):
        """
        Retourne le nom d'affichage (nom de scène ou nom complet)
        """
        if self.stage_name:
            return self.stage_name
        return self.user.get_full_name()

    def get_whatsapp_link(self, message=""):
        """
        Génère un lien WhatsApp avec message pré-rempli
        """
        phone = self.whatsapp_number or self.phone_number
        if not phone:
            return None

        # Nettoyer le numéro de téléphone
        clean_phone = "".join(filter(str.isdigit, phone))
        if not clean_phone.startswith("237"):
            clean_phone = "237" + clean_phone

        if message:
            import urllib.parse

            encoded_message = urllib.parse.quote(message)
            return f"https://wa.me/{clean_phone}?text={encoded_message}"

        return f"https://wa.me/{clean_phone}"

    def increment_views(self):
        """
        Incrémente le compteur de vues du profil
        """
        self.profile_views += 1
        self.save(update_fields=["profile_views"])

    def update_rating_average(self):
        """
        Met à jour la note moyenne et le nombre total d'avis
        """
        from apps.reviews.models import Review

        reviews = Review.objects.filter(artist=self, is_public=True)
        total_reviews = reviews.count()

        if total_reviews > 0:
            total_rating = sum(review.rating for review in reviews)
            self.rating_average = total_rating / total_reviews
            self.total_reviews = total_reviews
        else:
            self.rating_average = 0.00
            self.total_reviews = 0

        self.save(update_fields=["rating_average", "total_reviews"])


class OrganizerProfile(models.Model):
    """
    Profil pour les organisateurs d'événements
    """

    ORGANIZATION_TYPE_CHOICES = [
        ("individual", _("Particulier")),
        ("company", _("Entreprise")),
        ("church", _("Église")),
        ("association", _("Association")),
        ("event_agency", _("Agence événementielle")),
        ("other", _("Autre")),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="organizer_profile",
        verbose_name=_("Utilisateur"),
    )
    phone_number = models.CharField(
        _("Numéro de téléphone"),
        max_length=20,
        help_text=_("Numéro de téléphone principal"),
    )
    whatsapp_number = models.CharField(
        _("Numéro WhatsApp"),
        max_length=20,
        blank=True,
        help_text=_("Numéro WhatsApp pour contact direct"),
    )
    organization_name = models.CharField(
        _("Nom de l'organisation"),
        max_length=200,
        blank=True,
        help_text=_("Nom de l'entreprise, église, association, etc."),
    )
    organization_type = models.CharField(
        _("Type d'organisation"),
        max_length=20,
        choices=ORGANIZATION_TYPE_CHOICES,
        default="individual",
        help_text=_("Type d'organisation ou particulier"),
    )
    bio = models.TextField(
        _("Description de l'organisation"),
        blank=True,
        help_text=_("Description de votre organisation, vos activités et vos valeurs"),
    )
    profile_picture = models.ImageField(
        _("Photo de profil"),
        upload_to="profiles/organizers/",
        blank=True,
        null=True,
        help_text=_("Photo de profil ou logo de l'organisation"),
    )
    website = models.URLField(
        _("Site web"), blank=True, help_text=_("Site web de l'organisation (optionnel)")
    )
    address = models.TextField(
        _("Adresse"), blank=True, help_text=_("Adresse complète de l'organisation")
    )
    city = models.CharField(
        _("Ville"), max_length=100, help_text=_("Ville de résidence ou siège social")
    )
    region = models.CharField(
        _("Région"), max_length=100, help_text=_("Région du Cameroun")
    )
    profile_views = models.PositiveIntegerField(
        _("Vues du profil"),
        default=0,
        help_text=_("Nombre de fois que le profil a été consulté"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié le"), auto_now=True)

    class Meta:
        verbose_name = _("Profil Organisateur")
        verbose_name_plural = _("Profils Organisateurs")
        db_table = "accounts_organizer_profile"
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["region"]),
            models.Index(fields=["organization_type"]),
        ]

    def __str__(self):
        return self.get_display_name()

    def get_display_name(self):
        """
        Retourne le nom d'affichage (nom d'organisation ou nom complet)
        """
        if self.organization_name:
            return self.organization_name
        return self.user.get_full_name()

    def get_whatsapp_link(self, message=""):
        """
        Génère un lien WhatsApp avec message pré-rempli
        """
        phone = self.whatsapp_number or self.phone_number
        if not phone:
            return None

        # Nettoyer le numéro de téléphone
        clean_phone = "".join(filter(str.isdigit, phone))
        if not clean_phone.startswith("237"):
            clean_phone = "237" + clean_phone

        if message:
            import urllib.parse

            encoded_message = urllib.parse.quote(message)
            return f"https://wa.me/{clean_phone}?text={encoded_message}"

        return f"https://wa.me/{clean_phone}"

    def increment_views(self):
        """
        Incrémente le compteur de vues du profil
        """
        self.profile_views += 1
        self.save(update_fields=["profile_views"])


class EmailVerificationToken(models.Model):
    """
    Token pour la vérification d'email
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_tokens",
        verbose_name=_("Utilisateur"),
    )
    token = models.CharField(_("Token"), max_length=64, unique=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    expires_at = models.DateTimeField(_("Expire le"))
    is_used = models.BooleanField(_("Utilisé"), default=False)

    class Meta:
        verbose_name = _("Token de vérification email")
        verbose_name_plural = _("Tokens de vérification email")
        db_table = "accounts_email_verification_token"

    def __str__(self):
        return f"Token pour {self.user.email}"

    def is_expired(self):
        """
        Vérifie si le token a expiré
        """
        return timezone.now() > self.expires_at

    def is_valid(self):
        """
        Vérifie si le token est valide (non utilisé et non expiré)
        """
        return not self.is_used and not self.is_expired()
