"""
Settings package pour TalentZik
"""

import os
from decouple import config

# Déterminer l'environnement
ENVIRONMENT = config('DJANGO_ENV', default='development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'development':
    from .development import *
else:
    from .development import *
    
print(f"🔧 Configuration chargée: {ENVIRONMENT}")