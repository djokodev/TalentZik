"""
Filtres de template pour les fichiers média
"""

from django import template

register = template.Library()


@register.filter
def class_name(obj):
    """
    Retourne le nom de la classe d'un objet
    Usage: {{ object|class_name }}
    """
    return obj.__class__.__name__


@register.filter
def file_type_icon(obj):
    """
    Retourne l'icône FontAwesome appropriée selon le type de fichier
    """
    class_name = obj.__class__.__name__
    icons = {
        'AudioFile': 'fas fa-music',
        'VideoFile': 'fas fa-video',
        'PhotoFile': 'fas fa-image',
        'DocumentFile': 'fas fa-file-pdf',
    }
    return icons.get(class_name, 'fas fa-file')


@register.filter
def file_type_color(obj):
    """
    Retourne la couleur CSS appropriée selon le type de fichier
    """
    class_name = obj.__class__.__name__
    colors = {
        'AudioFile': 'blue',
        'VideoFile': 'purple',
        'PhotoFile': 'green',
        'DocumentFile': 'orange',
    }
    return colors.get(class_name, 'gray')


@register.filter
def format_file_size(size):
    """
    Formate la taille d'un fichier en format lisible
    """
    if not size:
        return "0 B"
    
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


@register.filter
def format_duration(seconds):
    """
    Formate une durée en secondes vers le format MM:SS ou HH:MM:SS
    """
    if not seconds:
        return "00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


@register.simple_tag
def file_type_badge(obj):
    """
    Génère un badge coloré selon le type de fichier
    """
    class_name = obj.__class__.__name__
    
    if class_name == 'AudioFile':
        return '<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">Audio</span>'
    elif class_name == 'VideoFile':
        return '<span class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">Vidéo</span>'
    elif class_name == 'PhotoFile':
        return '<span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Photo</span>'
    elif class_name == 'DocumentFile':
        return '<span class="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">Document</span>'
    else:
        return '<span class="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">Fichier</span>' 