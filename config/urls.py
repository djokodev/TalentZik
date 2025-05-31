"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Configuration de l'admin
admin.site.site_header = "TalentZik Administration"
admin.site.site_title = "TalentZik Admin"
admin.site.index_title = "Bienvenue dans l'administration TalentZik"

urlpatterns = [
    # Administration Django
    path("admin/", admin.site.urls),
    # Page d'accueil
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    # Applications
    path("accounts/", include("apps.accounts.urls")),
    path("artists/", include("apps.artists.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("media/", include("apps.media_files.urls")),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
