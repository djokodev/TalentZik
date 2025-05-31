"""
Services pour le traitement des fichiers multimédia avec FFmpeg
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
import ffmpeg

logger = logging.getLogger(__name__)


class MediaProcessingService:
    """Service principal pour le traitement des fichiers multimédia"""

    @staticmethod
    def get_watermark_path():
        """Retourne le chemin vers le logo TalentZik pour watermarking"""
        watermark_path = (
            Path(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0])
            / "images"
            / "watermark.png"
        )

        # Si le watermark n'existe pas, on en crée un simple
        if not watermark_path.exists():
            MediaProcessingService._create_default_watermark(watermark_path)

        return str(watermark_path)

    @staticmethod
    def _create_default_watermark(watermark_path):
        """Crée un watermark par défaut si il n'existe pas"""
        try:
            # Créer le dossier si nécessaire
            watermark_path.parent.mkdir(parents=True, exist_ok=True)

            # Créer une image simple avec le texte TalentZik
            from PIL import Image, ImageDraw, ImageFont

            img = Image.new("RGBA", (200, 50), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Utiliser une police par défaut
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()

            # Texte semi-transparent
            draw.text((10, 15), "TalentZik", fill=(255, 255, 255, 128), font=font)

            img.save(watermark_path)
            logger.info(f"Watermark par défaut créé : {watermark_path}")

        except Exception as e:
            logger.error(f"Erreur lors de la création du watermark : {e}")


class AudioProcessingService:
    """Service pour le traitement des fichiers audio"""

    @staticmethod
    def add_watermark_to_audio(audio_file_path, output_path=None):
        """
        Ajoute un watermark audio (intro/outro) à un fichier audio
        """
        try:
            if not output_path:
                # Générer un nom de fichier temporaire
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(audio_file_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(temp_dir, f"{name}_watermarked{ext}")

            # Pour le MVP, on va simplement normaliser l'audio et ajouter des métadonnées
            # Le watermarking audio complexe sera ajouté plus tard

            input_stream = ffmpeg.input(audio_file_path)

            # Normaliser le volume et ajouter des métadonnées
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                **{
                    "metadata": "title=TalentZik",
                    "metadata:s:a:0": "comment=Distribué par TalentZik - Plateforme musicale camerounaise",
                    "acodec": "mp3",
                    "audio_bitrate": "192k",
                },
            )

            # Exécuter la commande FFmpeg
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            logger.info(f"Watermark audio ajouté : {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors du watermarking audio : {e}")
            return None

    @staticmethod
    def get_audio_duration(audio_file_path):
        """Récupère la durée d'un fichier audio en secondes"""
        try:
            probe = ffmpeg.probe(audio_file_path)
            duration = float(probe["streams"][0]["duration"])
            return int(duration)
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la durée audio : {e}")
            return 0

    @staticmethod
    def convert_to_mp3(audio_file_path, output_path=None, bitrate="192k"):
        """Convertit un fichier audio en MP3"""
        try:
            if not output_path:
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(audio_file_path)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join(temp_dir, f"{name}.mp3")

            input_stream = ffmpeg.input(audio_file_path)
            output_stream = ffmpeg.output(
                input_stream, output_path, acodec="mp3", audio_bitrate=bitrate
            )

            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors de la conversion MP3 : {e}")
            return None


class VideoProcessingService:
    """Service pour le traitement des fichiers vidéo"""

    @staticmethod
    def add_watermark_to_video(video_file_path, output_path=None):
        """
        Ajoute un watermark vidéo à un fichier vidéo
        """
        try:
            if not output_path:
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(video_file_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(temp_dir, f"{name}_watermarked{ext}")

            watermark_path = MediaProcessingService.get_watermark_path()

            # Créer le stream d'entrée
            input_video = ffmpeg.input(video_file_path)
            input_watermark = ffmpeg.input(watermark_path)

            # Positionner le watermark en bas à droite avec transparence
            output_stream = ffmpeg.output(
                ffmpeg.overlay(
                    input_video,
                    input_watermark,
                    x="W-w-10",  # 10 pixels du bord droit
                    y="H-h-10",  # 10 pixels du bord bas
                ),
                output_path,
                vcodec="libx264",
                acodec="aac",
                **{"metadata": "comment=TalentZik - Plateforme musicale camerounaise"},
            )

            # Exécuter la commande FFmpeg
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            logger.info(f"Watermark vidéo ajouté : {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors du watermarking vidéo : {e}")
            return None

    @staticmethod
    def generate_thumbnail(video_file_path, output_path=None, time_offset=3):
        """
        Génère une miniature à partir d'une vidéo
        """
        try:
            if not output_path:
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(video_file_path)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join(temp_dir, f"{name}_thumb.jpg")

            # Extraire une frame à 3 secondes
            input_stream = ffmpeg.input(video_file_path, ss=time_offset)
            output_stream = ffmpeg.output(
                input_stream, output_path, vframes=1, format="image2", vcodec="mjpeg"
            )

            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            logger.info(f"Miniature générée : {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors de la génération de miniature : {e}")
            return None

    @staticmethod
    def get_video_duration(video_file_path):
        """Récupère la durée d'un fichier vidéo en secondes"""
        try:
            probe = ffmpeg.probe(video_file_path)
            duration = float(probe["streams"][0]["duration"])
            return int(duration)
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de la durée vidéo : {e}")
            return 0

    @staticmethod
    def compress_video(video_file_path, output_path=None, max_size_mb=50):
        """
        Compresse une vidéo pour réduire sa taille
        """
        try:
            if not output_path:
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(video_file_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(temp_dir, f"{name}_compressed{ext}")

            # Calcul du bitrate cible basé sur la taille max
            duration = VideoProcessingService.get_video_duration(video_file_path)
            if duration > 0:
                # Bitrate cible en kbps (avec marge de sécurité)
                target_bitrate = int((max_size_mb * 8 * 1024) / duration * 0.8)
                target_bitrate = max(target_bitrate, 500)  # Minimum 500 kbps
            else:
                target_bitrate = 1000  # Défaut 1000 kbps

            input_stream = ffmpeg.input(video_file_path)
            output_stream = ffmpeg.output(
                input_stream,
                output_path,
                vcodec="libx264",
                acodec="aac",
                video_bitrate=f"{target_bitrate}k",
                audio_bitrate="128k",
                preset="medium",
            )

            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)

            logger.info(f"Vidéo compressée : {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors de la compression vidéo : {e}")
            return None


class ImageProcessingService:
    """Service pour le traitement des images"""

    @staticmethod
    def optimize_image(
        image_file_path, output_path=None, max_width=1920, max_height=1080, quality=85
    ):
        """
        Optimise une image (redimensionnement et compression)
        """
        try:
            if not output_path:
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(image_file_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(temp_dir, f"{name}_optimized{ext}")

            with Image.open(image_file_path) as img:
                # Convertir en RGB si nécessaire
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(
                        img, mask=img.split()[-1] if img.mode == "RGBA" else None
                    )
                    img = background

                # Redimensionner si nécessaire
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                # Sauvegarder avec compression
                img.save(output_path, "JPEG", quality=quality, optimize=True)

            logger.info(f"Image optimisée : {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation d'image : {e}")
            return None

    @staticmethod
    def create_webp_version(image_file_path, output_path=None, quality=80):
        """
        Crée une version WebP d'une image pour une meilleure compression
        """
        try:
            if not output_path:
                temp_dir = tempfile.gettempdir()
                filename = os.path.basename(image_file_path)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join(temp_dir, f"{name}.webp")

            with Image.open(image_file_path) as img:
                # Convertir en RGB si nécessaire
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(
                        img, mask=img.split()[-1] if img.mode == "RGBA" else None
                    )
                    img = background

                # Sauvegarder en WebP
                img.save(output_path, "WEBP", quality=quality, optimize=True)

            logger.info(f"Version WebP créée : {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erreur lors de la création WebP : {e}")
            return None


class QuotaService:
    """Service pour la gestion des quotas de fichiers"""

    # Limites MVP
    MAX_AUDIO_FILES = 3
    MAX_VIDEO_FILES = 2
    MAX_PHOTO_FILES = 6
    MAX_DOCUMENT_FILES = 5

    @staticmethod
    def check_upload_permission(artist, file_type):
        """
        Vérifie si un artiste peut uploader un fichier de ce type
        """
        from .models import MediaFileQuota

        quota, created = MediaFileQuota.objects.get_or_create(artist=artist)

        if file_type == "audio":
            return quota.audio_count < QuotaService.MAX_AUDIO_FILES
        elif file_type == "video":
            return quota.video_count < QuotaService.MAX_VIDEO_FILES
        elif file_type == "photo":
            return quota.photo_count < QuotaService.MAX_PHOTO_FILES
        elif file_type == "document":
            return quota.document_count < QuotaService.MAX_DOCUMENT_FILES

        return False

    @staticmethod
    def get_quota_status(artist):
        """
        Retourne le statut des quotas pour un artiste
        """
        from .models import MediaFileQuota

        quota, created = MediaFileQuota.objects.get_or_create(artist=artist)

        return {
            "audio": {
                "used": quota.audio_count,
                "max": QuotaService.MAX_AUDIO_FILES,
                "can_upload": quota.audio_count < QuotaService.MAX_AUDIO_FILES,
            },
            "video": {
                "used": quota.video_count,
                "max": QuotaService.MAX_VIDEO_FILES,
                "can_upload": quota.video_count < QuotaService.MAX_VIDEO_FILES,
            },
            "photo": {
                "used": quota.photo_count,
                "max": QuotaService.MAX_PHOTO_FILES,
                "can_upload": quota.photo_count < QuotaService.MAX_PHOTO_FILES,
            },
            "document": {
                "used": quota.document_count,
                "max": QuotaService.MAX_DOCUMENT_FILES,
                "can_upload": quota.document_count < QuotaService.MAX_DOCUMENT_FILES,
            },
        }
