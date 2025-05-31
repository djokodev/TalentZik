from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings


def validate_file_size(file, max_size):
    """
    Validateur générique pour la taille des fichiers
    """
    if file.size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(
            _("La taille du fichier ne peut pas dépasser %(max_size)s MB."),
            params={"max_size": max_size_mb},
        )


def validate_audio_size(file):
    """Validateur pour les fichiers audio (25MB max)"""
    validate_file_size(file, settings.MAX_AUDIO_SIZE)


def validate_video_size(file):
    """Validateur pour les fichiers vidéo (100MB max)"""
    validate_file_size(file, settings.MAX_VIDEO_SIZE)


def validate_photo_size(file):
    """Validateur pour les photos (15MB max)"""
    validate_file_size(file, settings.MAX_PHOTO_SIZE)


def validate_document_size(file):
    """Validateur pour les documents (10MB max)"""
    validate_file_size(file, settings.MAX_DOCUMENT_SIZE)


class MediaFileBase(models.Model):
    """
    Modèle abstrait de base pour tous les fichiers multimédia
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        verbose_name=_("Artiste"),
    )
    title = models.CharField(
        _("Titre"), max_length=200, help_text=_("Titre du fichier")
    )
    description = models.TextField(
        _("Description"), blank=True, help_text=_("Description optionnelle du fichier")
    )
    upload_date = models.DateTimeField(_("Date d'upload"), auto_now_add=True)
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
        help_text=_("Indique si le fichier est visible publiquement"),
    )
    order = models.PositiveIntegerField(
        _("Ordre"), default=0, help_text=_("Ordre d'affichage dans le portfolio")
    )
    file_size = models.PositiveIntegerField(
        _("Taille du fichier"),
        help_text=_("Taille du fichier en bytes"),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ["order", "-upload_date"]

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, "size"):
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """
        Retourne la taille du fichier dans un format lisible
        """
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"


class AudioFile(MediaFileBase):
    """
    Fichiers audio des artistes
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        verbose_name=_("Artiste"),
        related_name="audio_files",
    )
    file = models.FileField(
        _("Fichier audio"),
        upload_to="media/audio/%Y/%m/",
        validators=[
            FileExtensionValidator(allowed_extensions=["mp3", "wav", "ogg", "m4a"]),
            validate_audio_size,
        ],
        help_text=_("Fichier audio (MP3, WAV, OGG, M4A - 25MB max)"),
    )
    duration = models.PositiveIntegerField(
        _("Durée"), null=True, blank=True, help_text=_("Durée en secondes")
    )

    class Meta:
        verbose_name = _("Fichier Audio")
        verbose_name_plural = _("Fichiers Audio")
        db_table = "media_files_audio"
        indexes = [
            models.Index(fields=["artist", "is_active"]),
            models.Index(fields=["upload_date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.artist.get_display_name()}"

    def get_duration_display(self):
        """
        Retourne la durée dans un format MM:SS
        """
        if not self.duration:
            return "00:00"

        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"


class VideoFile(MediaFileBase):
    """
    Fichiers vidéo des artistes
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        verbose_name=_("Artiste"),
        related_name="video_files",
    )
    file = models.FileField(
        _("Fichier vidéo"),
        upload_to="media/video/%Y/%m/",
        validators=[
            FileExtensionValidator(allowed_extensions=["mp4", "avi", "mov", "wmv"]),
            validate_video_size,
        ],
        blank=True,
        null=True,
        help_text=_("Fichier vidéo (MP4, AVI, MOV, WMV - 100MB max)"),
    )
    video_url = models.URLField(
        _("URL vidéo"),
        blank=True,
        help_text=_("Lien YouTube, Vimeo ou autre plateforme"),
    )
    thumbnail = models.ImageField(
        _("Miniature"),
        upload_to="media/video/thumbnails/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Image de prévisualisation de la vidéo"),
    )
    duration = models.PositiveIntegerField(
        _("Durée"), null=True, blank=True, help_text=_("Durée en secondes")
    )
    has_watermark = models.BooleanField(
        _("Filigrane ajouté"),
        default=False,
        help_text=_("Indique si le filigrane a été ajouté à la vidéo"),
    )

    class Meta:
        verbose_name = _("Fichier Vidéo")
        verbose_name_plural = _("Fichiers Vidéo")
        db_table = "media_files_video"
        indexes = [
            models.Index(fields=["artist", "is_active"]),
            models.Index(fields=["upload_date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.artist.get_display_name()}"

    def clean(self):
        super().clean()
        if not self.file and not self.video_url:
            raise ValidationError(
                _("Vous devez fournir soit un fichier vidéo soit une URL.")
            )

    def get_duration_display(self):
        """
        Retourne la durée dans un format MM:SS
        """
        if not self.duration:
            return "00:00"

        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_video_source(self):
        """
        Retourne la source de la vidéo (fichier local ou URL externe)
        """
        if self.file:
            return "local"
        elif self.video_url:
            if "youtube.com" in self.video_url or "youtu.be" in self.video_url:
                return "youtube"
            elif "vimeo.com" in self.video_url:
                return "vimeo"
            else:
                return "external"
        return None


class PhotoFile(MediaFileBase):
    """
    Photos des artistes
    """

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        verbose_name=_("Artiste"),
        related_name="photo_files",
    )
    file = models.ImageField(
        _("Photo"),
        upload_to="media/photos/%Y/%m/",
        validators=[validate_photo_size],
        help_text=_("Image (JPG, PNG, GIF - 15MB max)"),
    )
    is_profile_picture = models.BooleanField(
        _("Photo de profil"),
        default=False,
        help_text=_("Indique si cette photo est utilisée comme photo de profil"),
    )

    class Meta:
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
        db_table = "media_files_photo"
        indexes = [
            models.Index(fields=["artist", "is_active"]),
            models.Index(fields=["is_profile_picture"]),
            models.Index(fields=["upload_date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.artist.get_display_name()}"

    def save(self, *args, **kwargs):
        # Si cette photo est définie comme photo de profil,
        # désactiver les autres photos de profil de cet artiste
        if self.is_profile_picture:
            PhotoFile.objects.filter(
                artist=self.artist, is_profile_picture=True
            ).exclude(pk=self.pk).update(is_profile_picture=False)

        super().save(*args, **kwargs)


class DocumentFile(MediaFileBase):
    """
    Documents des artistes (partitions, press-kit, etc.)
    """

    DOCUMENT_TYPE_CHOICES = [
        ("partition", _("Partition")),
        ("press_kit", _("Press-kit")),
        ("contract", _("Contrat type")),
        ("rider", _("Rider technique")),
        ("biography", _("Biographie")),
        ("other", _("Autre")),
    ]

    artist = models.ForeignKey(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        verbose_name=_("Artiste"),
        related_name="documents",
    )
    file = models.FileField(
        _("Document"),
        upload_to="media/documents/%Y/%m/",
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
            validate_document_size,
        ],
        help_text=_("Document PDF uniquement (10MB max)"),
    )
    document_type = models.CharField(
        _("Type de document"),
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default="other",
        help_text=_("Type de document"),
    )

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        db_table = "media_files_document"
        indexes = [
            models.Index(fields=["artist", "is_active"]),
            models.Index(fields=["document_type"]),
            models.Index(fields=["upload_date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.artist.get_display_name()}"


class MediaFileQuota(models.Model):
    """
    Suivi des quotas de fichiers par artiste
    """

    artist = models.OneToOneField(
        "accounts.ArtistProfile",
        on_delete=models.CASCADE,
        related_name="media_quota",
        verbose_name=_("Artiste"),
    )
    audio_count = models.PositiveIntegerField(_("Nombre de fichiers audio"), default=0)
    video_count = models.PositiveIntegerField(_("Nombre de fichiers vidéo"), default=0)
    photo_count = models.PositiveIntegerField(_("Nombre de photos"), default=0)
    document_count = models.PositiveIntegerField(_("Nombre de documents"), default=0)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Quota de Médias")
        verbose_name_plural = _("Quotas de Médias")
        db_table = "media_files_quota"

    def __str__(self):
        return f"Quota de {self.artist.get_display_name()}"

    def can_upload_audio(self):
        """Vérifie si l'artiste peut uploader un fichier audio"""
        return self.audio_count < settings.MAX_AUDIO_FILES

    def can_upload_video(self):
        """Vérifie si l'artiste peut uploader une vidéo"""
        return self.video_count < settings.MAX_VIDEO_FILES

    def can_upload_photo(self):
        """Vérifie si l'artiste peut uploader une photo"""
        return self.photo_count < settings.MAX_PHOTO_FILES

    def can_upload_document(self):
        """Vérifie si l'artiste peut uploader un document"""
        return self.document_count < settings.MAX_DOCUMENT_FILES

    def update_counts(self):
        """Met à jour les compteurs basés sur les fichiers actifs"""
        self.audio_count = AudioFile.objects.filter(
            artist=self.artist, is_active=True
        ).count()
        self.video_count = VideoFile.objects.filter(
            artist=self.artist, is_active=True
        ).count()
        self.photo_count = PhotoFile.objects.filter(
            artist=self.artist, is_active=True
        ).count()
        self.document_count = DocumentFile.objects.filter(
            artist=self.artist, is_active=True
        ).count()
        self.save()
