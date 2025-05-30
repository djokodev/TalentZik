"""
URLs pour l'application media_files (gestion des fichiers multimédia)
"""

from django.urls import path
from . import views

app_name = "media_files"

urlpatterns = [
    # Upload de fichiers
    path("upload/audio/", views.AudioUploadView.as_view(), name="upload_audio"),
    path("upload/video/", views.VideoUploadView.as_view(), name="upload_video"),
    path("upload/photo/", views.PhotoUploadView.as_view(), name="upload_photo"),
    path(
        "upload/document/", views.DocumentUploadView.as_view(), name="upload_document"
    ),
    # Gestion des fichiers
    path("my-files/", views.MyFilesView.as_view(), name="my_files"),
    path("audio/<int:pk>/edit/", views.EditAudioView.as_view(), name="edit_audio"),
    path("video/<int:pk>/edit/", views.EditVideoView.as_view(), name="edit_video"),
    path("photo/<int:pk>/edit/", views.EditPhotoView.as_view(), name="edit_photo"),
    path(
        "document/<int:pk>/edit/",
        views.EditDocumentView.as_view(),
        name="edit_document",
    ),
    # Suppression
    path(
        "audio/<int:pk>/delete/", views.DeleteAudioView.as_view(), name="delete_audio"
    ),
    path(
        "video/<int:pk>/delete/", views.DeleteVideoView.as_view(), name="delete_video"
    ),
    path(
        "photo/<int:pk>/delete/", views.DeletePhotoView.as_view(), name="delete_photo"
    ),
    path(
        "document/<int:pk>/delete/",
        views.DeleteDocumentView.as_view(),
        name="delete_document",
    ),
]
