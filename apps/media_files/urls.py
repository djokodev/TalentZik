"""
URLs pour l'application media_files (portfolio multimédia)
"""

from django.urls import path
from . import views

app_name = "media_files"

urlpatterns = [
    # Vue principale
    path("", views.MyFilesView.as_view(), name="my_files"),
    # Alias pour portfolio (compatibilité avec les templates)
    path("portfolio/", views.MyFilesView.as_view(), name="portfolio"),
    # Upload de fichiers
    path("upload/audio/", views.AudioUploadView.as_view(), name="upload_audio"),
    path("upload/video/", views.VideoUploadView.as_view(), name="upload_video"),
    path("upload/photo/", views.PhotoUploadView.as_view(), name="upload_photo"),
    path(
        "upload/document/", views.DocumentUploadView.as_view(), name="upload_document"
    ),
    # Édition de fichiers
    path("edit/audio/<int:pk>/", views.EditAudioView.as_view(), name="edit_audio"),
    path("edit/video/<int:pk>/", views.EditVideoView.as_view(), name="edit_video"),
    path("edit/photo/<int:pk>/", views.EditPhotoView.as_view(), name="edit_photo"),
    path(
        "edit/document/<int:pk>/",
        views.EditDocumentView.as_view(),
        name="edit_document",
    ),
    # Suppression de fichiers
    path(
        "delete/audio/<int:pk>/", views.DeleteAudioView.as_view(), name="delete_audio"
    ),
    path(
        "delete/video/<int:pk>/", views.DeleteVideoView.as_view(), name="delete_video"
    ),
    path(
        "delete/photo/<int:pk>/", views.DeletePhotoView.as_view(), name="delete_photo"
    ),
    path(
        "delete/document/<int:pk>/",
        views.DeleteDocumentView.as_view(),
        name="delete_document",
    ),
    # API pour les statistiques
    path("api/stats/", views.MediaStatsAPIView.as_view(), name="api_stats"),
]
