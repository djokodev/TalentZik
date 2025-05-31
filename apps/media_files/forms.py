"""
Formulaires pour l'upload et la gestion des fichiers multimédia
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from .models import AudioFile, VideoFile, PhotoFile, DocumentFile
from .services import QuotaService


class BaseMediaFileForm(forms.ModelForm):
    """Formulaire de base pour tous les fichiers multimédia"""

    def __init__(self, *args, **kwargs):
        self.artist = kwargs.pop("artist", None)
        super().__init__(*args, **kwargs)

        # Styling des champs
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update(
                    {
                        "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    }
                )
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update(
                    {
                        "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                        "rows": 4,
                    }
                )
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update(
                    {
                        "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                    }
                )


class AudioFileForm(BaseMediaFileForm):
    """Formulaire pour l'upload de fichiers audio"""

    class Meta:
        model = AudioFile
        fields = ["title", "description", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].help_text = "Nom de votre morceau (ex: 'Mon nouveau hit')"
        self.fields["description"].help_text = (
            "Décrivez votre morceau, les collaborations, le style..."
        )
        self.fields["file"].help_text = (
            "Formats acceptés: MP3, WAV, OGG, M4A (max 25MB)"
        )

        # Champs requis
        self.fields["title"].required = True
        self.fields["file"].required = True

    def clean_file(self):
        """Validation personnalisée pour les fichiers audio"""
        file = self.cleaned_data.get("file")

        if file:
            # Vérifier le quota
            if self.artist and not QuotaService.check_upload_permission(
                self.artist, "audio"
            ):
                raise ValidationError(
                    f"Vous avez atteint la limite de {QuotaService.MAX_AUDIO_FILES} fichiers audio. "
                    "Supprimez un fichier existant pour en ajouter un nouveau."
                )

            # Vérifier la taille (25MB max)
            if file.size > 25 * 1024 * 1024:
                raise ValidationError("Le fichier audio ne doit pas dépasser 25 MB.")

            # Vérifier l'extension
            allowed_extensions = [".mp3", ".wav", ".ogg", ".m4a"]
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise ValidationError(
                    "Format non supporté. Utilisez MP3, WAV, OGG ou M4A."
                )

        return file

    def save(self, commit=True):
        """Sauvegarde avec association à l'artiste"""
        instance = super().save(commit=False)
        if self.artist:
            instance.artist = self.artist
        if commit:
            instance.save()
        return instance


class VideoFileForm(BaseMediaFileForm):
    """Formulaire pour l'upload de fichiers vidéo"""

    video_url = forms.URLField(
        label="Ou lien vidéo",
        required=False,
        help_text="Lien YouTube, Vimeo ou autre (alternatif au fichier)",
        widget=forms.URLInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "https://www.youtube.com/watch?v=...",
            }
        ),
    )

    class Meta:
        model = VideoFile
        fields = ["title", "description", "file", "video_url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].help_text = (
            "Titre de votre vidéo (ex: 'Clip officiel - Mon hit')"
        )
        self.fields["description"].help_text = (
            "Décrivez votre vidéo, les collaborations, le contexte..."
        )
        self.fields["file"].help_text = (
            "Formats acceptés: MP4, AVI, MOV, WMV (max 100MB)"
        )
        self.fields["file"].required = False  # Pas requis si URL fournie

        # Champs requis
        self.fields["title"].required = True

    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        video_url = cleaned_data.get("video_url")

        # Au moins un des deux doit être fourni
        if not file and not video_url:
            raise ValidationError(
                "Vous devez fournir soit un fichier vidéo soit une URL."
            )

        return cleaned_data

    def clean_file(self):
        """Validation personnalisée pour les fichiers vidéo"""
        file = self.cleaned_data.get("file")

        if file:
            # Vérifier le quota
            if self.artist and not QuotaService.check_upload_permission(
                self.artist, "video"
            ):
                raise ValidationError(
                    f"Vous avez atteint la limite de {QuotaService.MAX_VIDEO_FILES} fichiers vidéo. "
                    "Supprimez un fichier existant pour en ajouter un nouveau."
                )

            # Vérifier la taille (100MB max)
            if file.size > 100 * 1024 * 1024:
                raise ValidationError("Le fichier vidéo ne doit pas dépasser 100 MB.")

            # Vérifier l'extension
            allowed_extensions = [".mp4", ".avi", ".mov", ".wmv"]
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise ValidationError(
                    "Format non supporté. Utilisez MP4, AVI, MOV ou WMV."
                )

        return file

    def save(self, commit=True):
        """Sauvegarde avec association à l'artiste"""
        instance = super().save(commit=False)
        if self.artist:
            instance.artist = self.artist
        if commit:
            instance.save()
        return instance


class PhotoFileForm(BaseMediaFileForm):
    """Formulaire pour l'upload de photos"""

    is_profile_picture = forms.BooleanField(
        label="Utiliser comme photo de profil",
        required=False,
        help_text="Cette photo remplacera votre photo de profil actuelle",
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            }
        ),
    )

    class Meta:
        model = PhotoFile
        fields = ["title", "description", "file", "is_profile_picture"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].help_text = (
            "Titre de votre photo (ex: 'En concert à Douala')"
        )
        self.fields["description"].help_text = (
            "Contexte de la photo, lieu, événement..."
        )
        self.fields["file"].help_text = "Formats acceptés: JPG, PNG, GIF (max 15MB)"

        # Champs requis
        self.fields["title"].required = True
        self.fields["file"].required = True

    def clean_file(self):
        """Validation personnalisée pour les photos"""
        file = self.cleaned_data.get("file")

        if file:
            # Vérifier le quota
            if self.artist and not QuotaService.check_upload_permission(
                self.artist, "photo"
            ):
                raise ValidationError(
                    f"Vous avez atteint la limite de {QuotaService.MAX_PHOTO_FILES} photos. "
                    "Supprimez une photo existante pour en ajouter une nouvelle."
                )

            # Vérifier la taille (15MB max)
            if file.size > 15 * 1024 * 1024:
                raise ValidationError("La photo ne doit pas dépasser 15 MB.")

            # Vérifier l'extension
            allowed_extensions = [".jpg", ".jpeg", ".png", ".gif"]
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise ValidationError("Format non supporté. Utilisez JPG, PNG ou GIF.")

        return file

    def save(self, commit=True):
        """Sauvegarde avec association à l'artiste"""
        instance = super().save(commit=False)
        if self.artist:
            instance.artist = self.artist
        if commit:
            instance.save()
        return instance


class DocumentFileForm(BaseMediaFileForm):
    """Formulaire pour l'upload de documents"""

    document_type = forms.ChoiceField(
        label="Type de document",
        choices=DocumentFile.DOCUMENT_TYPE_CHOICES,
        help_text="Catégorie du document que vous uploadez",
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            }
        ),
    )

    class Meta:
        model = DocumentFile
        fields = ["title", "description", "file", "document_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].help_text = (
            "Nom du document (ex: 'Ma biographie officielle')"
        )
        self.fields["description"].help_text = "Description du contenu du document"
        self.fields["file"].help_text = "PDF uniquement (max 10MB)"

        # Champs requis
        self.fields["title"].required = True
        self.fields["file"].required = True
        self.fields["document_type"].required = True

    def clean_file(self):
        """Validation personnalisée pour les documents"""
        file = self.cleaned_data.get("file")

        if file:
            # Vérifier le quota
            if self.artist and not QuotaService.check_upload_permission(
                self.artist, "document"
            ):
                raise ValidationError(
                    f"Vous avez atteint la limite de {QuotaService.MAX_DOCUMENT_FILES} documents. "
                    "Supprimez un document existant pour en ajouter un nouveau."
                )

            # Vérifier la taille (10MB max)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("Le document ne doit pas dépasser 10 MB.")

            # Vérifier l'extension
            if not file.name.lower().endswith(".pdf"):
                raise ValidationError("Seuls les fichiers PDF sont acceptés.")

        return file

    def save(self, commit=True):
        """Sauvegarde avec association à l'artiste"""
        instance = super().save(commit=False)
        if self.artist:
            instance.artist = self.artist
        if commit:
            instance.save()
        return instance


class MediaFileEditForm(forms.ModelForm):
    """Formulaire pour éditer les informations d'un fichier existant"""

    class Meta:
        fields = ["title", "description", "is_active", "order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Styling des champs
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update(
                    {
                        "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    }
                )
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update(
                    {
                        "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                        "rows": 3,
                    }
                )
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(
                    {
                        "class": "h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    }
                )
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update(
                    {
                        "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    }
                )

        # Aide contextuelle
        self.fields["title"].help_text = "Titre affiché publiquement"
        self.fields["description"].help_text = "Description visible par les visiteurs"
        self.fields["is_active"].help_text = "Décochez pour masquer temporairement"
        self.fields["order"].help_text = "Ordre d'affichage (0 = premier)"


class AudioFileEditForm(MediaFileEditForm):
    """Formulaire d'édition spécifique aux fichiers audio"""

    class Meta(MediaFileEditForm.Meta):
        model = AudioFile


class VideoFileEditForm(MediaFileEditForm):
    """Formulaire d'édition spécifique aux fichiers vidéo"""

    video_url = forms.URLField(
        label="URL vidéo",
        required=False,
        help_text="Lien YouTube, Vimeo ou autre",
        widget=forms.URLInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
                "placeholder": "https://www.youtube.com/watch?v=...",
            }
        ),
    )

    class Meta(MediaFileEditForm.Meta):
        model = VideoFile
        fields = MediaFileEditForm.Meta.fields + ["video_url"]


class PhotoFileEditForm(MediaFileEditForm):
    """Formulaire d'édition spécifique aux photos"""

    is_profile_picture = forms.BooleanField(
        label="Utiliser comme photo de profil",
        required=False,
        help_text="Cette photo remplacera votre photo de profil actuelle",
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            }
        ),
    )

    class Meta(MediaFileEditForm.Meta):
        model = PhotoFile
        fields = MediaFileEditForm.Meta.fields + ["is_profile_picture"]


class DocumentFileEditForm(MediaFileEditForm):
    """Formulaire d'édition spécifique aux documents"""

    document_type = forms.ChoiceField(
        label="Type de document",
        choices=DocumentFile.DOCUMENT_TYPE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            }
        ),
    )

    class Meta(MediaFileEditForm.Meta):
        model = DocumentFile
        fields = MediaFileEditForm.Meta.fields + ["document_type"]


class BulkActionForm(forms.Form):
    """Formulaire pour les actions en lot sur les fichiers"""

    ACTION_CHOICES = [
        ("activate", "Activer les fichiers sélectionnés"),
        ("deactivate", "Désactiver les fichiers sélectionnés"),
        ("delete", "Supprimer les fichiers sélectionnés"),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            }
        ),
    )

    selected_files = forms.CharField(widget=forms.HiddenInput())

    def clean_selected_files(self):
        """Validation des IDs de fichiers sélectionnés"""
        selected = self.cleaned_data.get("selected_files", "")

        if not selected:
            raise ValidationError("Aucun fichier sélectionné.")

        try:
            # Convertir la chaîne d'IDs en liste d'entiers
            file_ids = [int(id.strip()) for id in selected.split(",") if id.strip()]
            if not file_ids:
                raise ValidationError("Aucun fichier valide sélectionné.")
            return file_ids
        except ValueError:
            raise ValidationError("IDs de fichiers invalides.")

        return file_ids
