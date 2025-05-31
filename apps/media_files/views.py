"""
Vues pour la gestion des fichiers multimédia avec traitement FFmpeg
"""

import os
import tempfile
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
)
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.urls import reverse_lazy, reverse

from .models import AudioFile, VideoFile, PhotoFile, DocumentFile, MediaFileQuota
from .forms import (
    AudioFileForm,
    VideoFileForm,
    PhotoFileForm,
    DocumentFileForm,
    AudioFileEditForm,
    VideoFileEditForm,
    PhotoFileEditForm,
    DocumentFileEditForm,
    BulkActionForm,
)
from .services import (
    AudioProcessingService,
    VideoProcessingService,
    ImageProcessingService,
    QuotaService,
)

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class MediaFilesMixin:
    """Mixin pour s'assurer que l'utilisateur est un artiste"""

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "artist_profile"):
            messages.error(
                request,
                "Vous devez être connecté comme artiste pour accéder à cette page.",
            )
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def get_artist(self):
        """Retourne le profil artiste de l'utilisateur connecté"""
        return self.request.user.artist_profile


class MyFilesView(MediaFilesMixin, TemplateView):
    """Vue principale pour gérer tous les fichiers de l'artiste"""

    template_name = "media_files/portfolio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist = self.get_artist()

        # Récupérer tous les fichiers
        audio_files = AudioFile.objects.filter(artist=artist).order_by(
            "order", "-upload_date"
        )
        video_files = VideoFile.objects.filter(artist=artist).order_by(
            "order", "-upload_date"
        )
        photo_files = PhotoFile.objects.filter(artist=artist).order_by(
            "order", "-upload_date"
        )
        document_files = DocumentFile.objects.filter(artist=artist).order_by(
            "order", "-upload_date"
        )

        # Statistiques des quotas
        quota_status = QuotaService.get_quota_status(artist)

        context.update(
            {
                "audio_files": audio_files,
                "video_files": video_files,
                "photo_files": photo_files,
                "document_files": document_files,
                "quota_status": quota_status,
                "page_title": "Mes fichiers multimédia",
                "bulk_form": BulkActionForm(),
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        """Gestion des actions en lot"""
        bulk_form = BulkActionForm(request.POST)

        if bulk_form.is_valid():
            action = bulk_form.cleaned_data["action"]
            file_ids = bulk_form.cleaned_data["selected_files"]

            try:
                if action == "activate":
                    self._bulk_activate(file_ids)
                    messages.success(
                        request, f"{len(file_ids)} fichier(s) activé(s) avec succès."
                    )
                elif action == "deactivate":
                    self._bulk_deactivate(file_ids)
                    messages.success(
                        request, f"{len(file_ids)} fichier(s) désactivé(s) avec succès."
                    )
                elif action == "delete":
                    self._bulk_delete(file_ids)
                    messages.success(
                        request, f"{len(file_ids)} fichier(s) supprimé(s) avec succès."
                    )

            except Exception as e:
                logger.error(f"Erreur lors de l'action en lot : {e}")
                messages.error(request, "Une erreur s'est produite lors de l'action.")

        return redirect("media_files:my_files")

    def _bulk_activate(self, file_ids):
        """Active les fichiers sélectionnés"""
        artist = self.get_artist()
        for model in [AudioFile, VideoFile, PhotoFile, DocumentFile]:
            model.objects.filter(id__in=file_ids, artist=artist).update(is_active=True)

    def _bulk_deactivate(self, file_ids):
        """Désactive les fichiers sélectionnés"""
        artist = self.get_artist()
        for model in [AudioFile, VideoFile, PhotoFile, DocumentFile]:
            model.objects.filter(id__in=file_ids, artist=artist).update(is_active=False)

    def _bulk_delete(self, file_ids):
        """Supprime les fichiers sélectionnés"""
        artist = self.get_artist()
        with transaction.atomic():
            for model in [AudioFile, VideoFile, PhotoFile, DocumentFile]:
                files_to_delete = model.objects.filter(id__in=file_ids, artist=artist)
                for file_obj in files_to_delete:
                    # Supprimer le fichier physique
                    if hasattr(file_obj, "file") and file_obj.file:
                        try:
                            file_obj.file.delete(save=False)
                        except:
                            pass
                    file_obj.delete()

            # Mettre à jour les quotas
            quota, _ = MediaFileQuota.objects.get_or_create(artist=artist)
            quota.update_counts()


class AudioUploadView(MediaFilesMixin, CreateView):
    """Vue d'upload de fichiers audio"""

    model = AudioFile
    form_class = AudioFileForm
    template_name = "media_files/upload_audio.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_form_kwargs(self):
        """Passer l'artiste au formulaire"""
        kwargs = super().get_form_kwargs()
        kwargs["artist"] = self.get_artist()
        return kwargs

    def form_valid(self, form):
        """Traitement du fichier audio avec FFmpeg"""
        try:
            with transaction.atomic():
                # Sauvegarder temporairement
                audio_file = form.save(commit=False)
                audio_file.artist = self.get_artist()

                # Traitement du fichier audio
                if audio_file.file:
                    # Obtenir la durée
                    duration = AudioProcessingService.get_audio_duration(
                        audio_file.file.path
                    )
                    audio_file.duration = duration

                    # Ajouter watermark (métadonnées pour le MVP)
                    watermarked_path = AudioProcessingService.add_watermark_to_audio(
                        audio_file.file.path
                    )

                    if watermarked_path and os.path.exists(watermarked_path):
                        # Remplacer le fichier original par la version watermarkée
                        with open(watermarked_path, "rb") as f:
                            watermarked_content = ContentFile(f.read())
                            audio_file.file.save(
                                os.path.basename(watermarked_path),
                                watermarked_content,
                                save=False,
                            )

                        # Nettoyer le fichier temporaire
                        os.unlink(watermarked_path)

                audio_file.save()

                # Mettre à jour les quotas
                quota, _ = MediaFileQuota.objects.get_or_create(
                    artist=self.get_artist()
                )
                quota.update_counts()

                messages.success(
                    self.request,
                    f"Fichier audio '{audio_file.title}' uploadé avec succès ! "
                    f"Durée: {audio_file.get_duration_display()}",
                )

        except Exception as e:
            logger.error(f"Erreur lors de l'upload audio : {e}")
            messages.error(
                self.request,
                "Une erreur s'est produite lors du traitement de votre fichier audio.",
            )
            return self.form_invalid(form)

        return super().form_valid(form)


class VideoUploadView(MediaFilesMixin, CreateView):
    """Vue d'upload de fichiers vidéo"""

    model = VideoFile
    form_class = VideoFileForm
    template_name = "media_files/upload_video.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_form_kwargs(self):
        """Passer l'artiste au formulaire"""
        kwargs = super().get_form_kwargs()
        kwargs["artist"] = self.get_artist()
        return kwargs

    def form_valid(self, form):
        """Traitement du fichier vidéo avec FFmpeg"""
        try:
            with transaction.atomic():
                video_file = form.save(commit=False)
                video_file.artist = self.get_artist()

                # Traitement du fichier vidéo si uploadé (pas pour les URLs)
                if video_file.file and hasattr(video_file.file, "path"):
                    # Vérifier que le fichier_size est défini pour les fichiers uploadés
                    if hasattr(video_file.file, "size") and video_file.file.size:
                        video_file.file_size = video_file.file.size

                    # Obtenir la durée
                    try:
                        duration = VideoProcessingService.get_video_duration(
                            video_file.file.path
                        )
                        video_file.duration = duration
                    except Exception as e:
                        logger.warning(
                            f"Impossible d'obtenir la durée de la vidéo: {e}"
                        )

                    # Générer une miniature
                    try:
                        thumbnail_path = VideoProcessingService.generate_thumbnail(
                            video_file.file.path
                        )

                        if thumbnail_path and os.path.exists(thumbnail_path):
                            with open(thumbnail_path, "rb") as f:
                                thumbnail_content = ContentFile(f.read())
                                video_file.thumbnail.save(
                                    f"thumb_{os.path.basename(thumbnail_path)}",
                                    thumbnail_content,
                                    save=False,
                                )
                            os.unlink(thumbnail_path)
                    except Exception as e:
                        logger.warning(f"Impossible de générer la miniature: {e}")

                    # Ajouter watermark
                    try:
                        watermarked_path = (
                            VideoProcessingService.add_watermark_to_video(
                                video_file.file.path
                            )
                        )

                        if watermarked_path and os.path.exists(watermarked_path):
                            # Remplacer le fichier original
                            with open(watermarked_path, "rb") as f:
                                watermarked_content = ContentFile(f.read())
                                video_file.file.save(
                                    os.path.basename(watermarked_path),
                                    watermarked_content,
                                    save=False,
                                )

                            video_file.has_watermark = True
                            os.unlink(watermarked_path)
                    except Exception as e:
                        logger.warning(f"Impossible d'ajouter le watermark: {e}")

                elif video_file.video_url:
                    # Pour les URLs (YouTube, etc.), définir file_size à 0
                    video_file.file_size = 0

                video_file.save()

                # Mettre à jour les quotas
                quota, _ = MediaFileQuota.objects.get_or_create(
                    artist=self.get_artist()
                )
                quota.update_counts()

                if video_file.video_url:
                    messages.success(
                        self.request,
                        f"Lien vidéo '{video_file.title}' ajouté avec succès !",
                    )
                else:
                    messages.success(
                        self.request,
                        f"Fichier vidéo '{video_file.title}' uploadé avec succès !",
                    )

        except Exception as e:
            logger.error(f"Erreur lors de l'upload vidéo : {e}")
            messages.error(
                self.request,
                "Une erreur s'est produite lors du traitement de votre fichier vidéo.",
            )
            return self.form_invalid(form)

        return super().form_valid(form)


class PhotoUploadView(MediaFilesMixin, CreateView):
    """Vue d'upload de photos"""

    model = PhotoFile
    form_class = PhotoFileForm
    template_name = "media_files/upload_photo.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_form_kwargs(self):
        """Passer l'artiste au formulaire"""
        kwargs = super().get_form_kwargs()
        kwargs["artist"] = self.get_artist()
        return kwargs

    def form_valid(self, form):
        """Traitement de l'image avec optimisation"""
        try:
            with transaction.atomic():
                photo_file = form.save(commit=False)
                photo_file.artist = self.get_artist()

                # Optimiser l'image
                if photo_file.file:
                    optimized_path = ImageProcessingService.optimize_image(
                        photo_file.file.path
                    )

                    if optimized_path and os.path.exists(optimized_path):
                        # Remplacer par la version optimisée
                        with open(optimized_path, "rb") as f:
                            optimized_content = ContentFile(f.read())
                            photo_file.file.save(
                                os.path.basename(optimized_path),
                                optimized_content,
                                save=False,
                            )
                        os.unlink(optimized_path)

                photo_file.save()

                # Mettre à jour la photo de profil si demandé
                if form.cleaned_data.get("is_profile_picture"):
                    artist = self.get_artist()
                    artist.profile_picture = photo_file.file
                    artist.save(update_fields=["profile_picture"])

                # Mettre à jour les quotas
                quota, _ = MediaFileQuota.objects.get_or_create(
                    artist=self.get_artist()
                )
                quota.update_counts()

                messages.success(
                    self.request, f"Photo '{photo_file.title}' uploadée avec succès !"
                )

        except Exception as e:
            logger.error(f"Erreur lors de l'upload photo : {e}")
            messages.error(
                self.request,
                "Une erreur s'est produite lors du traitement de votre photo.",
            )
            return self.form_invalid(form)

        return super().form_valid(form)


class DocumentUploadView(MediaFilesMixin, CreateView):
    """Vue d'upload de documents"""

    model = DocumentFile
    form_class = DocumentFileForm
    template_name = "media_files/upload_document.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_form_kwargs(self):
        """Passer l'artiste au formulaire"""
        kwargs = super().get_form_kwargs()
        kwargs["artist"] = self.get_artist()
        return kwargs

    def form_valid(self, form):
        """Sauvegarde du document"""
        try:
            with transaction.atomic():
                document_file = form.save(commit=False)
                document_file.artist = self.get_artist()
                document_file.save()

                # Mettre à jour les quotas
                quota, _ = MediaFileQuota.objects.get_or_create(
                    artist=self.get_artist()
                )
                quota.update_counts()

                messages.success(
                    self.request,
                    f"Document '{document_file.title}' uploadé avec succès !",
                )

        except Exception as e:
            logger.error(f"Erreur lors de l'upload document : {e}")
            messages.error(
                self.request,
                "Une erreur s'est produite lors de l'upload de votre document.",
            )
            return self.form_invalid(form)

        return super().form_valid(form)


# Vues d'édition


class EditAudioView(MediaFilesMixin, UpdateView):
    """Vue d'édition d'un fichier audio"""

    model = AudioFile
    form_class = AudioFileEditForm
    template_name = "media_files/edit_audio.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_queryset(self):
        """Limiter aux fichiers de l'artiste connecté"""
        return AudioFile.objects.filter(artist=self.get_artist())

    def form_valid(self, form):
        messages.success(self.request, "Fichier audio mis à jour avec succès !")
        return super().form_valid(form)


class EditVideoView(MediaFilesMixin, UpdateView):
    """Vue d'édition d'un fichier vidéo"""

    model = VideoFile
    form_class = VideoFileEditForm
    template_name = "media_files/edit_video.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_queryset(self):
        """Limiter aux fichiers de l'artiste connecté"""
        return VideoFile.objects.filter(artist=self.get_artist())

    def form_valid(self, form):
        messages.success(self.request, "Fichier vidéo mis à jour avec succès !")
        return super().form_valid(form)


class EditPhotoView(MediaFilesMixin, UpdateView):
    """Vue d'édition d'une photo"""

    model = PhotoFile
    form_class = PhotoFileEditForm
    template_name = "media_files/edit_photo.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_queryset(self):
        """Limiter aux fichiers de l'artiste connecté"""
        return PhotoFile.objects.filter(artist=self.get_artist())

    def form_valid(self, form):
        # Mettre à jour la photo de profil si demandé
        if form.cleaned_data.get("is_profile_picture"):
            artist = self.get_artist()
            artist.profile_picture = form.instance.file
            artist.save(update_fields=["profile_picture"])

        messages.success(self.request, "Photo mise à jour avec succès !")
        return super().form_valid(form)


class EditDocumentView(MediaFilesMixin, UpdateView):
    """Vue d'édition d'un document"""

    model = DocumentFile
    form_class = DocumentFileEditForm
    template_name = "media_files/edit_document.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_queryset(self):
        """Limiter aux fichiers de l'artiste connecté"""
        return DocumentFile.objects.filter(artist=self.get_artist())

    def form_valid(self, form):
        messages.success(self.request, "Document mis à jour avec succès !")
        return super().form_valid(form)


# Vues de suppression


class DeleteAudioView(MediaFilesMixin, DeleteView):
    """Vue de suppression d'un fichier audio"""

    model = AudioFile
    template_name = "media_files/delete_confirm.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_queryset(self):
        """Limiter aux fichiers de l'artiste connecté"""
        return AudioFile.objects.filter(artist=self.get_artist())

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().delete(request, *args, **kwargs)

            # Mettre à jour les quotas
            quota, _ = MediaFileQuota.objects.get_or_create(artist=self.get_artist())
            quota.update_counts()

            messages.success(request, "Fichier audio supprimé avec succès !")
            return response


class DeleteVideoView(MediaFilesMixin, DeleteView):
    """Vue de suppression d'un fichier vidéo"""

    model = VideoFile
    template_name = "media_files/delete_confirm.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_queryset(self):
        return VideoFile.objects.filter(artist=self.get_artist())

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().delete(request, *args, **kwargs)
            quota, _ = MediaFileQuota.objects.get_or_create(artist=self.get_artist())
            quota.update_counts()
            messages.success(request, "Fichier vidéo supprimé avec succès !")
            return response


class DeletePhotoView(MediaFilesMixin, DeleteView):
    """Vue de suppression d'une photo"""

    model = PhotoFile
    template_name = "media_files/delete_confirm.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_queryset(self):
        return PhotoFile.objects.filter(artist=self.get_artist())

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().delete(request, *args, **kwargs)
            quota, _ = MediaFileQuota.objects.get_or_create(artist=self.get_artist())
            quota.update_counts()
            messages.success(request, "Photo supprimée avec succès !")
            return response


class DeleteDocumentView(MediaFilesMixin, DeleteView):
    """Vue de suppression d'un document"""

    model = DocumentFile
    template_name = "media_files/delete_confirm.html"
    success_url = reverse_lazy("media_files:my_files")

    def get_queryset(self):
        return DocumentFile.objects.filter(artist=self.get_artist())

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().delete(request, *args, **kwargs)
            quota, _ = MediaFileQuota.objects.get_or_create(artist=self.get_artist())
            quota.update_counts()
            messages.success(request, "Document supprimé avec succès !")
            return response


# API Views pour les statistiques


class MediaStatsAPIView(MediaFilesMixin, TemplateView):
    """API pour les statistiques des fichiers"""

    def get(self, request, *args, **kwargs):
        artist = self.get_artist()
        quota_status = QuotaService.get_quota_status(artist)

        # Statistiques détaillées
        stats = {
            "quotas": quota_status,
            "total_files": (
                quota_status["audio"]["used"]
                + quota_status["video"]["used"]
                + quota_status["photo"]["used"]
                + quota_status["document"]["used"]
            ),
            "storage_used": self._calculate_storage_used(artist),
        }

        return JsonResponse(stats)

    def _calculate_storage_used(self, artist):
        """Calcule l'espace de stockage utilisé en MB"""
        total_bytes = 0

        for model in [AudioFile, VideoFile, PhotoFile, DocumentFile]:
            files = model.objects.filter(artist=artist)
            total_bytes += sum(f.file_size for f in files if f.file_size)

        return round(total_bytes / (1024 * 1024), 2)  # Convertir en MB
