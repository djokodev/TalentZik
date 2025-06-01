"""
Modèles pour les données de référence musicales et les relations artistes
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class MusicGenre(models.Model):
    """
    Genres musicaux disponibles sur la plateforme
    """

    name = models.CharField(
        _("Nom"), max_length=100, unique=True, help_text=_("Nom du genre musical")
    )
    slug = models.SlugField(_("Slug"), max_length=100, unique=True, blank=True)
    description = models.TextField(
        _("Description"), blank=True, help_text=_("Description du genre musical")
    )
    is_traditional = models.BooleanField(
        _("Genre traditionnel"),
        default=False,
        help_text=_("Indique si c'est un genre traditionnel camerounais/africain"),
    )
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
        help_text=_("Indique si le genre est disponible pour sélection"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Genre Musical")
        verbose_name_plural = _("Genres Musicaux")
        db_table = "artists_music_genre"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_traditional"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ArtistRole(models.Model):
    """
    Rôles/spécialités des artistes (DJ, Chanteur, Arrangeur, etc.)
    """

    name = models.CharField(
        _("Nom"), max_length=100, unique=True, help_text=_("Nom du rôle/spécialité")
    )
    slug = models.SlugField(_("Slug"), max_length=100, unique=True, blank=True)
    description = models.TextField(
        _("Description"), blank=True, help_text=_("Description du rôle/spécialité")
    )
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
        help_text=_("Indique si le rôle est disponible pour sélection"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Rôle d'Artiste")
        verbose_name_plural = _("Rôles d'Artistes")
        db_table = "artists_artist_role"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Instrument(models.Model):
    """
    Instruments de musique disponibles sur la plateforme
    """

    CATEGORY_CHOICES = [
        ("traditional", _("Traditionnel")),
        ("modern", _("Moderne")),
    ]

    name = models.CharField(
        _("Nom"), max_length=100, unique=True, help_text=_("Nom de l'instrument")
    )
    slug = models.SlugField(_("Slug"), max_length=100, unique=True, blank=True)
    description = models.TextField(
        _("Description"), blank=True, help_text=_("Description de l'instrument")
    )
    category = models.CharField(
        _("Catégorie"),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="modern",
        help_text=_("Catégorie de l'instrument"),
    )
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
        help_text=_("Indique si l'instrument est disponible pour sélection"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Instrument")
        verbose_name_plural = _("Instruments")
        db_table = "artists_instrument"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_instrument_category(self):
        """Retourne la catégorie détaillée de l'instrument basée sur son nom et type"""
        # Mapping des instruments vers leurs catégories familiales
        category_mapping = {
            # Cordes traditionnelles
            "Harpe arquée": "Cordes traditionnelles",
            "Harpe-luth Sawa": "Cordes traditionnelles",
            "Mvet": "Cordes traditionnelles",
            "Nkuu": "Cordes traditionnelles",
            # Cordes modernes
            "Banjo": "Cordes modernes",
            "Contrebasse": "Cordes modernes",
            "Guitare acoustique": "Cordes modernes",
            "Guitare basse": "Cordes modernes",
            "Guitare électrique": "Cordes modernes",
            "Harpe classique": "Cordes modernes",
            "Mandoline": "Cordes modernes",
            "Ukulélé": "Cordes modernes",
            "Violon": "Cordes modernes",
            "Violoncelle": "Cordes modernes",
            # Vents traditionnels
            "Algaita": "Vents traditionnels",
            "Corne d'antilope": "Vents traditionnels",
            "Flûte en bambou": "Vents traditionnels",
            "Flûte peule": "Vents traditionnels",
            "Kakaki": "Vents traditionnels",
            "Sifflet rituel": "Vents traditionnels",
            # Vents modernes
            "Clarinette": "Vents modernes",
            "Flûte traversière": "Vents modernes",
            "Harmonica": "Vents modernes",
            "Hautbois": "Vents modernes",
            "Saxophone alto": "Vents modernes",
            "Saxophone soprano": "Vents modernes",
            "Saxophone ténor": "Vents modernes",
            "Trombone": "Vents modernes",
            "Trompette": "Vents modernes",
            "Tuba": "Vents modernes",
            # Percussions sacrées
            "Balafon": "Percussions sacrées",
            "Bendré": "Percussions sacrées",
            "Djembé": "Percussions sacrées",
            "Tam-tam royal": "Percussions sacrées",
            "Tambour parlant": "Percussions sacrées",
            # Percussions traditionnelles
            "Dum-dum": "Percussions traditionnelles",
            "Konga": "Percussions traditionnelles",
            "Maracas traditionnelles": "Percussions traditionnelles",
            "Mbole": "Percussions traditionnelles",
            "Nding": "Percussions traditionnelles",
            "Ndong-mo-ba": "Percussions traditionnelles",
            "Tam-tam": "Percussions traditionnelles",
            # Percussions modernes
            "Batterie complète": "Percussions modernes",
            "Bongos": "Percussions modernes",
            "Cajon": "Percussions modernes",
            "Cloches": "Percussions modernes",
            "Congas": "Percussions modernes",
            "Cymbales": "Percussions modernes",
            "Gong": "Percussions modernes",
            "Shaker": "Percussions modernes",
            "Tambourin": "Percussions modernes",
            "Triangle": "Percussions modernes",
            # Claviers et harmoniques
            "Accordéon": "Claviers et harmoniques",
            "Clavier MIDI": "Claviers et harmoniques",
            "Kalimba": "Claviers et harmoniques",
            "Orgue électronique": "Claviers et harmoniques",
            "Piano acoustique": "Claviers et harmoniques",
            "Piano électrique": "Claviers et harmoniques",
            "Sanza": "Claviers et harmoniques",
            "Synthétiseur": "Claviers et harmoniques",
            # Instruments électroniques
            "Boîte à rythmes": "Instruments électroniques",
            "Sampler": "Instruments électroniques",
            "Turntables": "Instruments électroniques",
        }

        return category_mapping.get(self.name, "Autres instruments")


class ArtistGenre(models.Model):
    """
    Relation Many-to-Many entre Artistes et Genres musicaux
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="genres",
        verbose_name=_("Artiste"),
    )
    genre = models.ForeignKey(
        MusicGenre,
        on_delete=models.CASCADE,
        related_name="artists",
        verbose_name=_("Genre"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Genre d'Artiste")
        verbose_name_plural = _("Genres d'Artistes")
        db_table = "artists_artist_genre"
        unique_together = ["artist", "genre"]
        indexes = [
            models.Index(fields=["artist"]),
            models.Index(fields=["genre"]),
        ]

    def __str__(self):
        return f"{self.artist.get_display_name()} - {self.genre.name}"


class ArtistRoleAssignment(models.Model):
    """
    Relation Many-to-Many entre Artistes et Rôles
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name=_("Artiste"),
    )
    role = models.ForeignKey(
        ArtistRole,
        on_delete=models.CASCADE,
        related_name="artists",
        verbose_name=_("Rôle"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Rôle d'Artiste")
        verbose_name_plural = _("Rôles d'Artistes")
        db_table = "artists_artist_role_assignment"
        unique_together = ["artist", "role"]
        indexes = [
            models.Index(fields=["artist"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.artist.get_display_name()} - {self.role.name}"


class ArtistInstrument(models.Model):
    """
    Relation Many-to-Many entre Artistes et Instruments avec niveau de maîtrise
    """

    PROFICIENCY_CHOICES = [
        ("beginner", _("Débutant")),
        ("intermediate", _("Intermédiaire")),
        ("advanced", _("Avancé")),
        ("expert", _("Expert")),
    ]

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="instruments",
        verbose_name=_("Artiste"),
    )
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name="artists",
        verbose_name=_("Instrument"),
    )
    proficiency_level = models.CharField(
        _("Niveau de maîtrise"),
        max_length=20,
        choices=PROFICIENCY_CHOICES,
        default="intermediate",
        help_text=_("Niveau de maîtrise de l'instrument"),
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Instrument d'Artiste")
        verbose_name_plural = _("Instruments d'Artistes")
        db_table = "artists_artist_instrument"
        unique_together = ["artist", "instrument"]
        indexes = [
            models.Index(fields=["artist"]),
            models.Index(fields=["instrument"]),
            models.Index(fields=["proficiency_level"]),
        ]

    def __str__(self):
        return f"{self.artist.get_display_name()} - {self.instrument.name} ({self.get_proficiency_level_display()})"


class ProfileView(models.Model):
    """
    Tracking des vues de profils d'artistes
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="profile_views_log",
        verbose_name=_("Artiste"),
    )
    viewer = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="viewed_profiles",
        verbose_name=_("Visiteur"),
    )
    viewer_ip = models.GenericIPAddressField(
        _("Adresse IP"), help_text=_("Adresse IP du visiteur")
    )
    referrer = models.URLField(
        _("Référent"), blank=True, null=True, help_text=_("URL de la page précédente")
    )
    viewed_at = models.DateTimeField(_("Vu le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Vue de Profil")
        verbose_name_plural = _("Vues de Profils")
        db_table = "artists_profile_view"
        indexes = [
            models.Index(fields=["artist"]),
            models.Index(fields=["viewed_at"]),
            models.Index(fields=["viewer_ip"]),
        ]

    def __str__(self):
        viewer_name = self.viewer.get_full_name() if self.viewer else "Anonyme"
        return f"Vue de {self.artist.get_display_name()} par {viewer_name}"


class WhatsAppClick(models.Model):
    """
    Tracking des clics sur les boutons WhatsApp
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="whatsapp_clicks",
        verbose_name=_("Artiste"),
    )
    clicker = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="whatsapp_clicks",
        verbose_name=_("Utilisateur"),
    )
    clicker_ip = models.GenericIPAddressField(
        _("Adresse IP"), help_text=_("Adresse IP de l'utilisateur")
    )
    clicked_at = models.DateTimeField(_("Cliqué le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Clic WhatsApp")
        verbose_name_plural = _("Clics WhatsApp")
        db_table = "artists_whatsapp_click"
        indexes = [
            models.Index(fields=["artist"]),
            models.Index(fields=["clicked_at"]),
            models.Index(fields=["clicker_ip"]),
        ]

    def __str__(self):
        clicker_name = self.clicker.get_full_name() if self.clicker else "Anonyme"
        return f"Clic WhatsApp pour {self.artist.get_display_name()} par {clicker_name}"


class SearchQuery(models.Model):
    """
    Tracking des recherches effectuées sur la plateforme
    """

    query = models.TextField(_("Requête"), help_text=_("Texte de la recherche"))
    filters_used = models.JSONField(
        _("Filtres utilisés"),
        default=dict,
        blank=True,
        help_text=_("Filtres appliqués lors de la recherche"),
    )
    results_count = models.PositiveIntegerField(
        _("Nombre de résultats"), help_text=_("Nombre de résultats retournés")
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="searches",
        verbose_name=_("Utilisateur"),
    )
    user_ip = models.GenericIPAddressField(
        _("Adresse IP"), help_text=_("Adresse IP de l'utilisateur")
    )
    searched_at = models.DateTimeField(_("Recherché le"), auto_now_add=True)

    class Meta:
        verbose_name = _("Requête de Recherche")
        verbose_name_plural = _("Requêtes de Recherche")
        db_table = "artists_search_query"
        indexes = [
            models.Index(fields=["searched_at"]),
            models.Index(fields=["user"]),
            models.Index(fields=["user_ip"]),
        ]

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else "Anonyme"
        return f"Recherche '{self.query}' par {user_name}"
