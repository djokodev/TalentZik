from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import Textarea

from .models import AudioFile, VideoFile, PhotoFile, DocumentFile, MediaFileQuota


# Inline pour les quotas
class MediaFileQuotaInline(admin.StackedInline):
    model = MediaFileQuota
    extra = 0
    readonly_fields = ("updated_at",)
    fieldsets = (
        (
            "Quotas actuels",
            {
                "fields": (
                    ("audio_count", "video_count"),
                    ("photo_count", "document_count"),
                    "updated_at",
                )
            },
        ),
    )


@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "artist_link",
        "duration_display",
        "file_size_display",
        "is_active_icon",
        "upload_date",
        "preview_audio",
    ]
    list_filter = [
        "is_active",
        "upload_date",
        "artist__user__date_joined",
        ("artist", admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = [
        "title",
        "description",
        "artist__stage_name",
        "artist__user__first_name",
        "artist__user__last_name",
        "artist__user__email",
    ]
    readonly_fields = [
        "upload_date",
        "file_size",
        "duration",
        "preview_audio",
        "file_info",
    ]
    list_per_page = 20
    date_hierarchy = "upload_date"

    fieldsets = (
        ("Informations générales", {"fields": ("title", "description", "artist")}),
        ("Fichier", {"fields": ("file", "preview_audio", "file_info")}),
        ("Paramètres", {"fields": ("is_active", "order")}),
        (
            "Métadonnées (lecture seule)",
            {
                "fields": ("duration", "file_size", "upload_date"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["activate_files", "deactivate_files", "reset_order"]

    def artist_link(self, obj):
        if obj.artist:
            url = reverse("admin:accounts_artistprofile_change", args=[obj.artist.pk])
            return format_html(
                '<a href="{}">{}</a>', url, obj.artist.get_display_name()
            )
        return "-"

    artist_link.short_description = "Artiste"
    artist_link.admin_order_field = "artist__stage_name"

    def duration_display(self, obj):
        if obj.duration:
            minutes = obj.duration // 60
            seconds = obj.duration % 60
            return format_html(
                '<span style="font-family: monospace;">{:02d}:{:02d}</span>',
                minutes,
                seconds,
            )
        return "-"

    duration_display.short_description = "Durée"
    duration_display.admin_order_field = "duration"

    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "-"

    file_size_display.short_description = "Taille"
    file_size_display.admin_order_field = "file_size"

    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Actif</span>')
        return format_html('<span style="color: red;">● Inactif</span>')

    is_active_icon.short_description = "Statut"
    is_active_icon.admin_order_field = "is_active"

    def preview_audio(self, obj):
        if obj.file:
            return format_html(
                '<audio controls style="max-width: 300px;">'
                '<source src="{}" type="audio/mpeg">'
                "Votre navigateur ne supporte pas l'audio."
                "</audio>",
                obj.file.url,
            )
        return "-"

    preview_audio.short_description = "Aperçu"

    def file_info(self, obj):
        if obj.file:
            return format_html(
                "<strong>Nom:</strong> {}<br>"
                '<strong>URL:</strong> <a href="{}" target="_blank">{}</a><br>'
                "<strong>Taille:</strong> {}",
                obj.file.name,
                obj.file.url,
                obj.file.url,
                self.file_size_display(obj),
            )
        return "-"

    file_info.short_description = "Informations du fichier"

    def activate_files(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} fichier(s) audio activé(s).")

    activate_files.short_description = "Activer les fichiers sélectionnés"

    def deactivate_files(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} fichier(s) audio désactivé(s).")

    deactivate_files.short_description = "Désactiver les fichiers sélectionnés"

    def reset_order(self, request, queryset):
        for i, obj in enumerate(queryset.order_by("upload_date")):
            obj.order = i
            obj.save(update_fields=["order"])
        self.message_user(
            request, f"Ordre réinitialisé pour {queryset.count()} fichier(s)."
        )

    reset_order.short_description = "Réinitialiser l'ordre"


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "artist_link",
        "video_source_display",
        "duration_display",
        "file_size_display",
        "has_watermark_icon",
        "is_active_icon",
        "upload_date",
    ]
    list_filter = [
        "is_active",
        "has_watermark",
        "upload_date",
        ("artist", admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = [
        "title",
        "description",
        "video_url",
        "artist__stage_name",
        "artist__user__first_name",
        "artist__user__last_name",
    ]
    readonly_fields = [
        "upload_date",
        "file_size",
        "duration",
        "preview_video",
        "file_info",
    ]

    fieldsets = (
        ("Informations générales", {"fields": ("title", "description", "artist")}),
        (
            "Source vidéo",
            {
                "fields": ("file", "video_url", "preview_video"),
                "description": "Choisissez soit un fichier à uploader, soit une URL externe",
            },
        ),
        ("Miniature", {"fields": ("thumbnail",), "classes": ("collapse",)}),
        ("Paramètres", {"fields": ("is_active", "order", "has_watermark")}),
        (
            "Métadonnées (lecture seule)",
            {
                "fields": ("duration", "file_size", "upload_date", "file_info"),
                "classes": ("collapse",),
            },
        ),
    )

    def artist_link(self, obj):
        if obj.artist:
            url = reverse("admin:accounts_artistprofile_change", args=[obj.artist.pk])
            return format_html(
                '<a href="{}">{}</a>', url, obj.artist.get_display_name()
            )
        return "-"

    artist_link.short_description = "Artiste"

    def video_source_display(self, obj):
        if obj.file:
            return format_html('<span style="color: blue;">📁 Fichier local</span>')
        elif obj.video_url:
            if "youtube" in obj.video_url.lower():
                return format_html('<span style="color: red;">▶️ YouTube</span>')
            elif "vimeo" in obj.video_url.lower():
                return format_html('<span style="color: green;">🎬 Vimeo</span>')
            else:
                return format_html('<span style="color: orange;">🔗 URL externe</span>')
        return "-"

    video_source_display.short_description = "Source"

    def duration_display(self, obj):
        if obj.duration:
            hours = obj.duration // 3600
            minutes = (obj.duration % 3600) // 60
            seconds = obj.duration % 60
            if hours > 0:
                return format_html(
                    '<span style="font-family: monospace;">{:02d}:{:02d}:{:02d}</span>',
                    hours,
                    minutes,
                    seconds,
                )
            else:
                return format_html(
                    '<span style="font-family: monospace;">{:02d}:{:02d}</span>',
                    minutes,
                    seconds,
                )
        return "-"

    duration_display.short_description = "Durée"

    def file_size_display(self, obj):
        if obj.file_size and obj.file_size > 0:
            if obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "-"

    file_size_display.short_description = "Taille"

    def has_watermark_icon(self, obj):
        if obj.has_watermark:
            return format_html('<span style="color: green;">🛡️ Protégé</span>')
        return format_html('<span style="color: gray;">— Non protégé</span>')

    has_watermark_icon.short_description = "Watermark"

    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Actif</span>')
        return format_html('<span style="color: red;">● Inactif</span>')

    is_active_icon.short_description = "Statut"

    def preview_video(self, obj):
        if obj.file:
            return format_html(
                '<video controls style="max-width: 300px; max-height: 200px;">'
                '<source src="{}" type="video/mp4">'
                "Votre navigateur ne supporte pas la vidéo."
                "</video>",
                obj.file.url,
            )
        elif obj.video_url:
            return format_html(
                '<a href="{}" target="_blank">🔗 Voir la vidéo externe</a>',
                obj.video_url,
            )
        return "-"

    preview_video.short_description = "Aperçu"

    def file_info(self, obj):
        info_parts = []
        if obj.file:
            info_parts.append(f"<strong>Fichier:</strong> {obj.file.name}")
            info_parts.append(
                f'<strong>URL:</strong> <a href="{obj.file.url}" target="_blank">{obj.file.url}</a>'
            )
        if obj.video_url:
            info_parts.append(
                f'<strong>URL externe:</strong> <a href="{obj.video_url}" target="_blank">{obj.video_url}</a>'
            )
        if obj.thumbnail:
            info_parts.append(
                f'<strong>Miniature:</strong> <a href="{obj.thumbnail.url}" target="_blank">Voir</a>'
            )
        return format_html("<br>".join(info_parts)) if info_parts else "-"

    file_info.short_description = "Informations détaillées"


@admin.register(PhotoFile)
class PhotoFileAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "artist_link",
        "thumbnail_preview",
        "is_profile_picture_icon",
        "file_size_display",
        "is_active_icon",
        "upload_date",
    ]
    list_filter = [
        "is_active",
        "is_profile_picture",
        "upload_date",
        ("artist", admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = [
        "title",
        "description",
        "artist__stage_name",
        "artist__user__first_name",
        "artist__user__last_name",
    ]
    readonly_fields = ["upload_date", "file_size", "image_preview", "file_info"]

    fieldsets = (
        ("Informations générales", {"fields": ("title", "description", "artist")}),
        ("Image", {"fields": ("file", "image_preview", "file_info")}),
        ("Paramètres", {"fields": ("is_active", "is_profile_picture", "order")}),
        (
            "Métadonnées (lecture seule)",
            {"fields": ("file_size", "upload_date"), "classes": ("collapse",)},
        ),
    )

    def artist_link(self, obj):
        if obj.artist:
            url = reverse("admin:accounts_artistprofile_change", args=[obj.artist.pk])
            return format_html(
                '<a href="{}">{}</a>', url, obj.artist.get_display_name()
            )
        return "-"

    artist_link.short_description = "Artiste"

    def thumbnail_preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.file.url,
            )
        return "-"

    thumbnail_preview.short_description = "Aperçu"

    def image_preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: contain; border: 1px solid #ddd; border-radius: 4px;" />',
                obj.file.url,
            )
        return "-"

    image_preview.short_description = "Prévisualisation"

    def is_profile_picture_icon(self, obj):
        if obj.is_profile_picture:
            return format_html('<span style="color: gold;">⭐ Photo de profil</span>')
        return format_html('<span style="color: gray;">— Photo normale</span>')

    is_profile_picture_icon.short_description = "Type"

    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "-"

    file_size_display.short_description = "Taille"

    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Actif</span>')
        return format_html('<span style="color: red;">● Inactif</span>')

    is_active_icon.short_description = "Statut"

    def file_info(self, obj):
        if obj.file:
            return format_html(
                "<strong>Nom:</strong> {}<br>"
                '<strong>URL:</strong> <a href="{}" target="_blank">{}</a><br>'
                "<strong>Taille:</strong> {}",
                obj.file.name,
                obj.file.url,
                obj.file.url,
                self.file_size_display(obj),
            )
        return "-"

    file_info.short_description = "Informations du fichier"


@admin.register(DocumentFile)
class DocumentFileAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "artist_link",
        "document_type_display",
        "file_size_display",
        "is_active_icon",
        "upload_date",
    ]
    list_filter = [
        "document_type",
        "is_active",
        "upload_date",
        ("artist", admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = [
        "title",
        "description",
        "artist__stage_name",
        "artist__user__first_name",
        "artist__user__last_name",
    ]
    readonly_fields = ["upload_date", "file_size", "file_info", "download_link"]

    fieldsets = (
        (
            "Informations générales",
            {"fields": ("title", "description", "artist", "document_type")},
        ),
        ("Document", {"fields": ("file", "download_link", "file_info")}),
        ("Paramètres", {"fields": ("is_active", "order")}),
        (
            "Métadonnées (lecture seule)",
            {"fields": ("file_size", "upload_date"), "classes": ("collapse",)},
        ),
    )

    def artist_link(self, obj):
        if obj.artist:
            url = reverse("admin:accounts_artistprofile_change", args=[obj.artist.pk])
            return format_html(
                '<a href="{}">{}</a>', url, obj.artist.get_display_name()
            )
        return "-"

    artist_link.short_description = "Artiste"

    def document_type_display(self, obj):
        type_icons = {
            "partition": "🎼",
            "press_kit": "📰",
            "contract": "📄",
            "rider": "⚙️",
            "biography": "📖",
            "other": "📋",
        }
        icon = type_icons.get(obj.document_type, "📄")
        return format_html("{} {}", icon, obj.get_document_type_display())

    document_type_display.short_description = "Type de document"

    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "-"

    file_size_display.short_description = "Taille"

    def is_active_icon(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">● Actif</span>')
        return format_html('<span style="color: red;">● Inactif</span>')

    is_active_icon.short_description = "Statut"

    def download_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" style="background: #007cba; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">📥 Télécharger le PDF</a>',
                obj.file.url,
            )
        return "-"

    download_link.short_description = "Téléchargement"

    def file_info(self, obj):
        if obj.file:
            return format_html(
                "<strong>Nom:</strong> {}<br>"
                '<strong>URL:</strong> <a href="{}" target="_blank">{}</a><br>'
                "<strong>Taille:</strong> {}",
                obj.file.name,
                obj.file.url,
                obj.file.url,
                self.file_size_display(obj),
            )
        return "-"

    file_info.short_description = "Informations du fichier"


@admin.register(MediaFileQuota)
class MediaFileQuotaAdmin(admin.ModelAdmin):
    list_display = [
        "artist_link",
        "audio_usage",
        "video_usage",
        "photo_usage",
        "document_usage",
        "total_files",
        "updated_at",
    ]
    list_filter = [
        "updated_at",
        ("artist", admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = [
        "artist__stage_name",
        "artist__user__first_name",
        "artist__user__last_name",
        "artist__user__email",
    ]
    readonly_fields = ["updated_at", "total_files", "quota_details"]

    fieldsets = (
        ("Artiste", {"fields": ("artist",)}),
        (
            "Quotas utilisés",
            {
                "fields": (
                    ("audio_count", "video_count"),
                    ("photo_count", "document_count"),
                    "total_files",
                )
            },
        ),
        (
            "Détails",
            {"fields": ("quota_details", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = ["refresh_quotas"]

    def artist_link(self, obj):
        if obj.artist:
            url = reverse("admin:accounts_artistprofile_change", args=[obj.artist.pk])
            return format_html(
                '<a href="{}">{}</a>', url, obj.artist.get_display_name()
            )
        return "-"

    artist_link.short_description = "Artiste"

    def audio_usage(self, obj):
        max_audio = 3  # À partir des settings
        percentage = (obj.audio_count / max_audio) * 100 if max_audio > 0 else 0
        color = (
            "red" if percentage >= 100 else "orange" if percentage >= 80 else "green"
        )
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.audio_count,
            max_audio,
            int(percentage),
        )

    audio_usage.short_description = "Audio"

    def video_usage(self, obj):
        max_video = 2
        percentage = (obj.video_count / max_video) * 100 if max_video > 0 else 0
        color = (
            "red" if percentage >= 100 else "orange" if percentage >= 80 else "green"
        )
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.video_count,
            max_video,
            int(percentage),
        )

    video_usage.short_description = "Vidéo"

    def photo_usage(self, obj):
        max_photo = 6
        percentage = (obj.photo_count / max_photo) * 100 if max_photo > 0 else 0
        color = (
            "red" if percentage >= 100 else "orange" if percentage >= 80 else "green"
        )
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.photo_count,
            max_photo,
            int(percentage),
        )

    photo_usage.short_description = "Photos"

    def document_usage(self, obj):
        max_document = 5
        percentage = (
            (obj.document_count / max_document) * 100 if max_document > 0 else 0
        )
        color = (
            "red" if percentage >= 100 else "orange" if percentage >= 80 else "green"
        )
        return format_html(
            '<span style="color: {};">{}/{} ({}%)</span>',
            color,
            obj.document_count,
            max_document,
            int(percentage),
        )

    document_usage.short_description = "Documents"

    def total_files(self, obj):
        total = obj.audio_count + obj.video_count + obj.photo_count + obj.document_count
        return format_html("<strong>{}</strong> fichiers", total)

    total_files.short_description = "Total"

    def quota_details(self, obj):
        details = []
        details.append(f"<strong>Audio:</strong> {obj.audio_count}/3 fichiers")
        details.append(f"<strong>Vidéo:</strong> {obj.video_count}/2 fichiers")
        details.append(f"<strong>Photos:</strong> {obj.photo_count}/6 fichiers")
        details.append(f"<strong>Documents:</strong> {obj.document_count}/5 fichiers")
        details.append(
            f'<strong>Dernière mise à jour:</strong> {obj.updated_at.strftime("%d/%m/%Y à %H:%M")}'
        )
        return format_html("<br>".join(details))

    quota_details.short_description = "Détails des quotas"

    def refresh_quotas(self, request, queryset):
        for quota in queryset:
            quota.update_counts()
        self.message_user(
            request, f"Quotas mis à jour pour {queryset.count()} artiste(s)."
        )

    refresh_quotas.short_description = "Actualiser les quotas"


# Configuration de l'admin
admin.site.site_header = "TalentZik Administration"
admin.site.site_title = "TalentZik Admin"
admin.site.index_title = "Gestion des Fichiers Média"
